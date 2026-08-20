import openai
import json
import pickle
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from prompt import Prompt_book, Prompt_case
from api_info import api_key, base_url


# ============================================
# 路径配置 - 统一管理所有文件路径
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DATA_FILE = os.path.join(BASE_DIR, 'statformbench.json')
MODEL_NAME_FILE = os.path.join(BASE_DIR, 'model_name0.txt')
OUTPUT_DIR = os.path.join(BASE_DIR, 'results')

# 输出文件路径
RESULT_FILE_BASE = 'all_models_result_other'

# 并发数设置
MAX_WORKERS = 10


def ensure_result_dir():
    """确保结果保存目录存在"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"结果将保存到: {os.path.abspath(OUTPUT_DIR)}")


def remove_error_rows():
    """删除输出CSV中所有错误行"""
    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")
    if os.path.exists(combined_csv):
        df = pd.read_csv(combined_csv)
        before_count = len(df)
        df_filtered = df[~df['output_json'].astype(str).str.startswith('错误')]
        after_count = len(df_filtered)
        removed_count = before_count - after_count
        if removed_count > 0:
            df_filtered.to_csv(combined_csv, index=False, encoding='utf-8-sig')
            print(f"已删除 {removed_count} 条错误记录，剩余 {after_count} 条有效记录")
        else:
            print("未发现错误记录，无需删除")
    else:
        print("结果文件不存在，无需删除错误行")


def get_output_path(filename):
    """获取输出文件的完整路径"""
    return os.path.join(OUTPUT_DIR, filename)


def read_model_names():
    """读取model_name.txt文件中的模型名称"""
    with open(MODEL_NAME_FILE, 'r', encoding='utf-8') as f:
        model_names = [line.strip() for line in f if line.strip()]
    return model_names


def process_data_description(data_description):
    """处理data_description_2字段，仅保留关键信息"""
    if not data_description:
        return data_description

    return data_description


def abstract_statistical_problem(input_data, model_name="gpt-4o", source="book"):
    """调用大模型API抽象统计问题"""
    if source == "case":
        prompt = f"{Prompt_case}\n\nquestion：\n{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\nPlease output the data in the required JSON format."
    else:
        prompt = f"{Prompt_book}\n\nquestion：\n{json.dumps(input_data, ensure_ascii=False, indent=2)}\n\nPlease output the data in the required JSON format."

    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional statistician"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            #extra_body={"chat_template_kwargs":{"enable_thinking":False}}

        )
        #print("=" * 70)
        #print(response)

        output = response.choices[0].message.content.strip()
        #print("=" * 70)
        #print(output)

        if output.startswith("```json"):
            output = output[7:]
        elif output.startswith("```"):
            output = output[3:]
        if output.endswith("```"):
            output = output[:-3]
        output = output.strip()

        prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') and response.usage else 0
        completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') and response.usage else 0

        return output, prompt_tokens, completion_tokens

    except Exception as e:
        return f"错误: {str(e)}", 0, 0


def process_sample_for_model(sample_key, sample_data, model_name):
    """为单个样本和模型处理数据"""
    input_data = sample_data['input']
    source = sample_data.get('source', 'book')

    try:
        output_json, prompt_tokens, completion_tokens = abstract_statistical_problem(input_data, model_name, source)

        result = {
            'sample_key': sample_key,
            'model_name': model_name,
            'input_data': json.dumps(input_data, ensure_ascii=False),
            'output_json': output_json,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens
        }

        return result

    except Exception as e:
        return {
            'sample_key': sample_key,
            'model_name': model_name,
            'input_data': json.dumps(input_data, ensure_ascii=False),
            'output_json': f"错误: {str(e)}",
            'prompt_tokens': 0,
            'completion_tokens': 0
        }


def load_existing_results():
    """加载已存在的结果，用于判断哪些样本已经处理过"""
    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")

    if os.path.exists(combined_csv):
        try:
            df = pd.read_csv(combined_csv)
            processed = set()
            for _, row in df.iterrows():
                try:
                    sample_key = str(row['sample_key'])
                    model_name = row['model_name']
                    processed.add((sample_key, model_name))
                except:
                    pass
            print(f"已加载 {len(processed)} 条已处理记录")
            return processed
        except:
            print("加载已存在结果失败，将重新处理所有样本")
            return set()
    else:
        print("未找到已存在的结果文件，将处理所有样本")
        return set()


def save_results(results, is_final=False):
    """保存结果到文件"""
    if not results:
        return

    df = pd.DataFrame(results)

    combined_pkl = get_output_path(f"{RESULT_FILE_BASE}.pkl")
    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")

    if os.path.exists(combined_csv):
        existing_df = pd.read_csv(combined_csv)
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['sample_key', 'model_name'], keep='last')
    else:
        combined_df = df

    combined_df.to_pickle(combined_pkl)
    combined_df.to_csv(combined_csv, index=False, encoding='utf-8-sig')

    print(f"\n已保存 {len(df)} 条记录到 {combined_csv}")
    print(f"当前总记录数: {len(combined_df)}")

    if is_final:
        model_names = df['model_name'].unique()
        for model_name in model_names:
            model_df = combined_df[combined_df['model_name'] == model_name]
            if len(model_df) > 0:
                safe_model_name = model_name.replace('/', '_').replace('\\', '_')
                filename = get_output_path(f"{safe_model_name}result.pkl")

                model_df.to_pickle(filename)
                model_df.to_csv(filename.replace('.pkl', '.csv'), index=False, encoding='utf-8-sig')

                print(f"模型 {model_name} 结果已保存到 {filename}")


def process_all_samples_parallel():
    """并行处理所有样本和模型"""
    ensure_result_dir()
    processed = load_existing_results()

    print(f"读取输入文件: {INPUT_DATA_FILE}")
    with open(INPUT_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    model_names = read_model_names()

    tasks = []
    for sample_key, sample_data in data.items():
        for model_name in model_names:
            if (str(sample_key), model_name) not in processed:
                tasks.append((sample_key, sample_data, model_name))

    print(f"开始并行处理: {len(tasks)} 个待处理任务")
    print(f"模型列表: {model_names}")
    print(f"并发数: {MAX_WORKERS}")

    results = []
    batch_size = 10
    total_tasks = len(tasks)
    completed_tasks = 0

    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, len(model_names))) as executor:
        future_to_task = {}

        for task in tasks:
            sample_key, sample_data, model_name = task
            future = executor.submit(process_sample_for_model, sample_key, sample_data, model_name)
            future_to_task[future] = (sample_key, model_name)

        for future in as_completed(future_to_task):
            sample_key, model_name = future_to_task[future]

            try:
                result = future.result()
                results.append(result)
                completed_tasks += 1

                print(f"进度: {completed_tasks}/{total_tasks} - 样本 {sample_key} - 模型 {model_name} - 完成")

                if len(results) >= batch_size:
                    save_results(results, is_final=False)
                    results = []

            except Exception as e:
                print(f"进度: {completed_tasks}/{total_tasks} - 样本 {sample_key} - 模型 {model_name} - 错误: {e}")

                error_result = {
                    'sample_key': sample_key,
                    'model_name': model_name,
                    'input_data': json.dumps(data[sample_key]['input'], ensure_ascii=False),
                    'output_json': f"错误: {str(e)}",
                    'prompt_tokens': 0,
                    'completion_tokens': 0
                }
                results.append(error_result)
                completed_tasks += 1

                if len(results) >= batch_size:
                    save_results(results, is_final=False)
                    results = []

            time.sleep(0.5)

    if results:
        save_results(results, is_final=True)

    print(f"\n处理完成！")
    print(f"总共处理了 {completed_tasks} 条记录")

    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")
    if os.path.exists(combined_csv):
        df = pd.read_csv(combined_csv)
        print(f"最终总记录数: {len(df)}")
        return df
    else:
        return None


def process_model_sequentially(model_name):
    """顺序处理单个模型的所有样本"""
    ensure_result_dir()

    print(f"\n开始处理模型: {model_name}")
    processed = load_existing_results()

    print(f"读取输入文件: {INPUT_DATA_FILE}")
    with open(INPUT_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = []
    for sample_key, sample_data in data.items():
        if (str(sample_key), model_name) not in processed:
            tasks.append((sample_key, sample_data))

    print(f"待处理任务数: {len(tasks)}")

    results = []
    batch_size = 10

    for i, (sample_key, sample_data) in enumerate(tasks):
        print(f"  进度: {i+1}/{len(tasks)} - 样本 {sample_key}")

        result = process_sample_for_model(sample_key, sample_data, model_name)
        results.append(result)

        if (i + 1) % batch_size == 0:
            save_results(results, is_final=False)
            results = []

        time.sleep(1)

    if results:
        save_results(results, is_final=True)

    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")
    if os.path.exists(combined_csv):
        df = pd.read_csv(combined_csv)
        model_df = df[df['model_name'] == model_name]
        if len(model_df) > 0:
            safe_model_name = model_name.replace('/', '_').replace('\\', '_')
            filename = get_output_path(f"{safe_model_name}result.pkl")

            model_df.to_pickle(filename)
            model_df.to_csv(filename.replace('.pkl', '.csv'), index=False, encoding='utf-8-sig')

            print(f"模型 {model_name} 处理完成！结果已保存到 {filename}")
            return model_df

    return None


if __name__ == "__main__":
    print("=" * 50)
    print("路径配置:")
    print(f"  基础目录: {BASE_DIR}")
    print(f"  输出目录: {OUTPUT_DIR}")
    print(f"  输入文件: {INPUT_DATA_FILE}")
    print(f"  模型列表: {MODEL_NAME_FILE}")
    print("=" * 50)

    remove_error_rows()

    df = process_all_samples_parallel()

    if df is not None:
        print("\n结果摘要:")
        print(f"总记录数: {len(df)}")
        print(f"模型数量: {df['model_name'].nunique()}")
        print(f"样本数量: {df['sample_key'].nunique()}")

        if 'prompt_tokens' in df.columns and 'completion_tokens' in df.columns:
            total_prompt = df['prompt_tokens'].sum()
            total_completion = df['completion_tokens'].sum()
            total_tokens = total_prompt + total_completion
            print(f"\nToken使用统计:")
            print(f"总Prompt Tokens: {total_prompt}")
            print(f"总Completion Tokens: {total_completion}")
            print(f"总Tokens: {total_tokens}")

        print("\n前3条记录:")
        print(df.head(3))

        print("\n数据框结构:")
        print(f"列名: {df.columns.tolist()}")
        print(f"形状: {df.shape}")