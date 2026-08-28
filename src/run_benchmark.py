import openai
import json
import pickle
import pandas as pd
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to sys.path to import config / prompts packages
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from prompts.prompts import Prompt_book, Prompt_case
from config.api_config import api_key, base_url


# ============================================
# Path configuration - centralized file path management
# ============================================
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
INPUT_DATA_FILE = os.path.join(DATA_DIR, 'statformbench.json')
MODEL_NAME_FILE = os.path.join(PROJECT_ROOT, 'config', 'models.txt')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'results')

# Output file path
RESULT_FILE_BASE = 'all_models_result_other'

# Concurrency settings
MAX_WORKERS = 10

# HuggingFace dataset repository
HF_REPO_ID = "THU-CongLab/StatFormBench"
HF_DATASET_FILES = ['statformbench.json', 'statformbench.pkl']


def ensure_dataset_files():
    """Download dataset files from HuggingFace if they are not present locally"""
    os.makedirs(DATA_DIR, exist_ok=True)

    missing_files = [f for f in HF_DATASET_FILES if not os.path.exists(os.path.join(DATA_DIR, f))]

    if not missing_files:
        print(f"Dataset files already exist in: {DATA_DIR}")
        return

    print(f"Missing dataset files: {missing_files}")
    print(f"Downloading from HuggingFace: https://huggingface.co/datasets/{HF_REPO_ID}")

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        raise ImportError(
            "huggingface_hub is required to download dataset files. "
            "Install it with: pip install huggingface_hub"
        )

    for filename in missing_files:
        print(f"  Downloading {filename} ...")
        downloaded_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=filename,
            repo_type="dataset",
            local_dir=DATA_DIR,
        )
        print(f"  Saved to: {downloaded_path}")

    print("Dataset files ready.")


def ensure_result_dir():
    """Ensure the output directory exists"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Results will be saved to: {os.path.abspath(OUTPUT_DIR)}")


def remove_error_rows():
    """Remove all error rows from the output CSV"""
    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")
    if os.path.exists(combined_csv):
        df = pd.read_csv(combined_csv)
        before_count = len(df)
        df_filtered = df[~df['output_json'].astype(str).str.startswith('错误')]
        after_count = len(df_filtered)
        removed_count = before_count - after_count
        if removed_count > 0:
            df_filtered.to_csv(combined_csv, index=False, encoding='utf-8-sig')
            print(f"Removed {removed_count} error records, {after_count} valid records remaining")
        else:
            print("No error records found, nothing to remove")
    else:
        print("Result file does not exist, no error rows to remove")


def get_output_path(filename):
    """Get the full path of an output file"""
    return os.path.join(OUTPUT_DIR, filename)


def read_model_names():
    """Read model names from models.txt"""
    with open(MODEL_NAME_FILE, 'r', encoding='utf-8') as f:
        model_names = [line.strip() for line in f if line.strip()]
    return model_names


def process_data_description(data_description):
    """Process the data_description_2 field, keeping only key information"""
    if not data_description:
        return data_description

    return data_description


def abstract_statistical_problem(input_data, model_name="gpt-4o", source="book"):
    """Call LLM API to abstract statistical problems"""
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
    """Process data for a single sample and model"""
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
    """Load existing results to determine which samples have already been processed"""
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
            print(f"Loaded {len(processed)} processed records")
            return processed
        except:
            print("Failed to load existing results, will reprocess all samples")
            return set()
    else:
        print("No existing result file found, will process all samples")
        return set()


def save_results(results, is_final=False):
    """Save results to file"""
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

    print(f"\nSaved {len(df)} records to {combined_csv}")
    print(f"Current total records: {len(combined_df)}")

    if is_final:
        model_names = df['model_name'].unique()
        for model_name in model_names:
            model_df = combined_df[combined_df['model_name'] == model_name]
            if len(model_df) > 0:
                safe_model_name = model_name.replace('/', '_').replace('\\', '_')
                filename = get_output_path(f"{safe_model_name}result.pkl")

                model_df.to_pickle(filename)
                model_df.to_csv(filename.replace('.pkl', '.csv'), index=False, encoding='utf-8-sig')

                print(f"Model {model_name} results saved to {filename}")


def process_all_samples_parallel():
    """Process all samples and models in parallel"""
    ensure_result_dir()
    processed = load_existing_results()

    print(f"Reading input file: {INPUT_DATA_FILE}")
    with open(INPUT_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    model_names = read_model_names()

    tasks = []
    for sample_key, sample_data in data.items():
        for model_name in model_names:
            if (str(sample_key), model_name) not in processed:
                tasks.append((sample_key, sample_data, model_name))

    print(f"Starting parallel processing: {len(tasks)} tasks to process")
    print(f"Model list: {model_names}")
    print(f"Concurrency: {MAX_WORKERS}")

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

                print(f"Progress: {completed_tasks}/{total_tasks} - sample {sample_key} - model {model_name} - completed")

                if len(results) >= batch_size:
                    save_results(results, is_final=False)
                    results = []

            except Exception as e:
                print(f"Progress: {completed_tasks}/{total_tasks} - sample {sample_key} - model {model_name} - error: {e}")

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

    print(f"\nProcessing complete!")
    print(f"Total processed {completed_tasks} records")

    combined_csv = get_output_path(f"{RESULT_FILE_BASE}.csv")
    if os.path.exists(combined_csv):
        df = pd.read_csv(combined_csv)
        print(f"Final total records: {len(df)}")
        return df
    else:
        return None


def process_model_sequentially(model_name):
    """Process all samples for a single model sequentially"""
    ensure_result_dir()

    print(f"\nStarting processing model: {model_name}")
    processed = load_existing_results()

    print(f"Reading input file: {INPUT_DATA_FILE}")
    with open(INPUT_DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = []
    for sample_key, sample_data in data.items():
        if (str(sample_key), model_name) not in processed:
            tasks.append((sample_key, sample_data))

    print(f"Tasks to process: {len(tasks)}")

    results = []
    batch_size = 10

    for i, (sample_key, sample_data) in enumerate(tasks):
        print(f"  Progress: {i+1}/{len(tasks)} - sample {sample_key}")

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

            print(f"Model {model_name} processing complete! Results saved to {filename}")
            return model_df

    return None


if __name__ == "__main__":
    print("=" * 50)
    print("Path configuration:")
    print(f"  Base directory: {PROJECT_ROOT}")
    print(f"  Output directory: {OUTPUT_DIR}")
    print(f"  Input file: {INPUT_DATA_FILE}")
    print(f"  Model list: {MODEL_NAME_FILE}")
    print("=" * 50)

    ensure_dataset_files()

    remove_error_rows()

    df = process_all_samples_parallel()

    if df is not None:
        print("\nResult summary:")
        print(f"Total records: {len(df)}")
        print(f"Number of models: {df['model_name'].nunique()}")
        print(f"Number of samples: {df['sample_key'].nunique()}")

        if 'prompt_tokens' in df.columns and 'completion_tokens' in df.columns:
            total_prompt = df['prompt_tokens'].sum()
            total_completion = df['completion_tokens'].sum()
            total_tokens = total_prompt + total_completion
            print(f"\nToken usage statistics:")
            print(f"Total Prompt Tokens: {total_prompt}")
            print(f"Total Completion Tokens: {total_completion}")
            print(f"Total Tokens: {total_tokens}")

        print("\nFirst 3 records:")
        print(df.head(3))

        print("\nDataFrame structure:")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Shape: {df.shape}")