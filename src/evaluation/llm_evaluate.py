import pandas as pd
import json
import os
import sys
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import openai

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from prompts.prompts import prompt_evaluate0
from config.api_config import api_key, base_url
from json_utils import extract_last_json_safe


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_evaluation_data():
    """Load evaluation sample data"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation_results', 'all_models_result_evaluated.csv')
    logger.info(f"Loading evaluation sample file: {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Successfully loaded {len(df)} samples")
    return df


def process_data_description(data_description):
    """Process data_description_2 field, keeping only key information"""
    if not data_description:
        return data_description

    # Check if it's a dictionary structure
    if isinstance(data_description, dict):
        # Process each dataset
        processed_description = {}
        for dataset_name, dataset_info in data_description.items():
            if isinstance(dataset_info, dict):
                # Keep only the specified four fields
                processed_dataset = {}
                if 'data_type' in dataset_info:
                    processed_dataset['data_type'] = dataset_info['data_type']
                if 'data_shape' in dataset_info:
                    processed_dataset['data_shape'] = dataset_info['data_shape']
                if 'variable_names' in dataset_info:
                    processed_dataset['variable_names'] = dataset_info['variable_names']
                if 'basic_statistics' in dataset_info:
                    processed_dataset['basic_statistics'] = dataset_info['basic_statistics']
                processed_description[dataset_name] = processed_dataset
            else:
                processed_description[dataset_name] = dataset_info
        return processed_description
    return data_description


def evaluate_with_llm(question_description, output_json, model_name="gpt-5-mini"):
    """
    Call LLM for evaluation

    Args:
        question_description (str): Question description (JSON format string)
        output_json (str): Statistical model to evaluate (JSON format string)
        model_name (str): Model name to use

    Returns:
        tuple: (evaluation_result, token_usage_dict)
            - evaluation_result: parsed evaluation result dict or None
            - token_usage_dict: dict containing input_tokens, output_tokens, total_tokens
    """
    try:
        # Parse question_description as dict
        try:
            input_data = json.loads(question_description)
        except:
            input_data = {}

        # Check and process data_description_2 field
        if 'data_description_2' in input_data:
            data_description_2 = input_data['data_description_2']
            # Calculate total character count
            data_desc_str = json.dumps(data_description_2, ensure_ascii=False)

            #logger.info(f"Detected data_description_2 field is too long ({len(data_desc_str)} characters), processing...")
                # Process data_description_2 field
            processed_data_description = process_data_description(data_description_2)
                # Check processed length
            processed_str = json.dumps(processed_data_description, ensure_ascii=False)
            logger.info(f"Processed length: {len(processed_str)} characters")
                # Update input_data
            input_data['data_description_2'] = processed_data_description
                # Reconvert to JSON string
            question_description = json.dumps(input_data, ensure_ascii=False, indent=2)

        # Build complete prompt
        prompt = f"{prompt_evaluate0}\n\nQuestion description (JSON):\n{question_description}\n\nStatistical model to evaluate (JSON):\n{output_json}\n\nPlease output the review report in the required JSON format:"

        # Call OpenAI API
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an experienced statistician and reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        # Extract model output
        output = response.choices[0].message.content.strip()

        # Get token usage
        token_usage = {
            'input_tokens': response.usage.prompt_tokens if hasattr(response, 'usage') and response.usage else 0,
            'output_tokens': response.usage.completion_tokens if hasattr(response, 'usage') and response.usage else 0,
            'total_tokens': response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
        }

        # Parse JSON output
        result = extract_last_json_safe(output)

        return result, token_usage

    except Exception as e:
        logger.error(f"LLM evaluation failed: {e}")
        return None, {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}


def validate_evaluation_result(result):
    """
    Validate whether model output meets the required format

    Args:
        result: parsed evaluation result

    Returns:
        tuple: (is_valid, error_message)
    """
    if result is None:
        return False, "Unable to parse JSON output"

    if not isinstance(result, dict):
        return False, "Output is not in dict format"

    # Check required fields
    required_fields = ['total_score', 'scores', 'comment']
    for field in required_fields:
        if field not in result:
            return False, f"Missing required field: {field}"

    # Check scores field
    if not isinstance(result['scores'], dict):
        return False, "scores field is not in dict format"

    required_score_fields = ['variable_role_abstraction', 'method_abstraction']
    for field in required_score_fields:
        if field not in result['scores']:
            return False, f"scores missing required field: {field}"

    # Check score range
    try:
        total_score = int(result['total_score'])
        if not (0 <= total_score <= 10):
            return False, f"total_score out of range (0-10): {total_score}"

        var_score = int(result['scores']['variable_role_abstraction'])
        if not (0 <= var_score <= 5):
            return False, f"variable_role_abstraction out of range (0-5): {var_score}"

        method_score = int(result['scores']['method_abstraction'])
        if not (0 <= method_score <= 5):
            return False, f"method_abstraction out of range (0-5): {method_score}"
    except (ValueError, TypeError) as e:
        return False, f"Score format error: {e}"

    return True, None


def process_single_sample(row_data):
    """
    Process evaluation of a single sample, with retry mechanism

    Args:
        row_data (tuple): (index, row) sample index and data

    Returns:
        dict: evaluation result
    """
    idx, row = row_data
    sample_key = row['sample_key']
    model_name = row['model_name']
    error_type = row['error_type']

    logger.info(f"Processing sample {idx}: sample_key={sample_key}, model={model_name}, error_type={error_type}")

    # Initialize result
    result = {
        'sample_key': sample_key,
        'model_name': model_name,
        'input_data': row['input_data'],
        'output_json': row['output_json'],
        'total_score': 0,
        'variable_role_abstraction': 0,
        'method_abstraction': 0,
        'comment': 'None',
        'input_tokens': 0,
        'output_tokens': 0,
        'total_tokens': 0,
        'evaluation_error': None
    }

    # Check error_type
    if error_type != 'successful':
        logger.info(f"Sample {idx} error_type is not successful, skipping LLM evaluation")
        result['evaluation_error'] = f"error_type={error_type}, no need to evaluate"
        return result

    # Retry mechanism: max 5 attempts
    max_retries = 5
    question_description = row['input_data']
    output_json = row['output_json']

    for attempt in range(1, max_retries + 1):
        logger.info(f"Sample {idx} attempt {attempt}/{max_retries} evaluation attempt")

        try:
            eval_result, token_usage = evaluate_with_llm(question_description, output_json)

            # Update token usage (cumulative)
            result['input_tokens'] += token_usage['input_tokens']
            result['output_tokens'] += token_usage['output_tokens']
            result['total_tokens'] += token_usage['total_tokens']

            # Validate result
            is_valid, error_message = validate_evaluation_result(eval_result)

            if is_valid:
                # Evaluation successful, update result and break loop
                result['total_score'] = int(eval_result['total_score'])
                result['variable_role_abstraction'] = int(eval_result['scores']['variable_role_abstraction'])
                result['method_abstraction'] = int(eval_result['scores']['method_abstraction'])
                result['comment'] = eval_result['comment']
                result['evaluation_error'] = None
                logger.info(f"Sample {idx} attempt {attempt} evaluation successful: total_score={result['total_score']}")
                break
            else:
                # Validation failed, record error
                result['evaluation_error'] = f"Attempt {attempt} failed - Result validation failed: {error_message}"
                logger.warning(f"Sample {idx} attempt {attempt} evaluation validation failed: {error_message}")

                # If retry attempts remain, continue to next attempt
                if attempt < max_retries:
                    logger.info(f"Sample {idx} will retry attempt {attempt + 1}")
                else:
                    logger.error(f"Sample {idx} reached max retry count {max_retries}, evaluation failed")

        except Exception as e:
            # Exception handling
            result['evaluation_error'] = f"Attempt {attempt} failed - Evaluation exception: {str(e)}"
            logger.error(f"Sample {idx} attempt {attempt} evaluation exception: {e}")

            # If retry attempts remain, continue to next attempt
            if attempt < max_retries:
                logger.info(f"Sample {idx} will retry attempt {attempt + 1}")
            else:
                logger.error(f"Sample {idx} reached max retry count {max_retries}, evaluation failed")

    return result


def save_batch_results(results, is_final=False, filename='evaluated0.csv'):
    """Save batch results to file, append mode"""
    if not results:
        return

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Determine save path
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation_results')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    # Save data in append mode
    if os.path.exists(output_path):
        # File exists, append mode (without header)
        df.to_csv(output_path, mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        # File does not exist, create new file with header
        df.to_csv(output_path, mode='w', header=True, index=False, encoding='utf-8-sig')

    if is_final:
        logger.info(f"\nFinal results saved to: {output_path}")
        # Read file to count total rows
        try:
            final_df = pd.read_csv(output_path)
            logger.info(f"Total records: {len(final_df)}")
        except:
            logger.info(f"Saved this batch {len(results)} records")
    else:
        logger.info(f"Appended {len(results)} records to {output_path}")


def show_statistics(final_df):
    """Display evaluation statistics"""
    logger.info("\n" + "=" * 60)
    logger.info("Evaluation completion statistics")
    logger.info("=" * 60)

    # Statistics
    successful_evaluations = len(final_df[final_df['evaluation_error'].isna()])
    failed_evaluations = len(final_df[final_df['evaluation_error'].notna()])

    logger.info(f"Total samples: {len(final_df)}")
    logger.info(f"Successfully evaluated: {successful_evaluations}")
    logger.info(f"Evaluation failed: {failed_evaluations}")

    # Score statistics
    if successful_evaluations > 0:
        logger.info("\nScore statistics:")
        logger.info(f"total_score - mean: {final_df['total_score'].mean():.2f}, std: {final_df['total_score'].std():.2f}")
        logger.info(f"variable_role_abstraction - mean: {final_df['variable_role_abstraction'].mean():.2f}, std: {final_df['variable_role_abstraction'].std():.2f}")
        logger.info(f"method_abstraction - mean: {final_df['method_abstraction'].mean():.2f}, std: {final_df['method_abstraction'].std():.2f}")

    # Token usage statistics
    total_input_tokens = final_df['input_tokens'].sum()
    total_output_tokens = final_df['output_tokens'].sum()
    total_tokens = final_df['total_tokens'].sum()

    logger.info(f"\nToken usage statistics:")
    logger.info(f"Total input tokens: {total_input_tokens}")
    logger.info(f"Total output tokens: {total_output_tokens}")
    logger.info(f"Total tokens: {total_tokens}")

    # Display first few results
    logger.info("\nFirst 5 evaluation results:")
    preview_columns = ['sample_key', 'model_name', 'total_score', 'variable_role_abstraction', 'method_abstraction']
    logger.info("\n" + str(final_df[preview_columns].head()))


def load_processed_samples(filename='evaluated0_newdata.csv'):
    """Load processed samples for checkpoint resume"""
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation_results', filename)
    processed_samples = set()

    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path)
            # Use combination of sample_key and model_name as unique identifier
            # Convert to string type uniformly for comparison to avoid type mismatch
            for _, row in existing_df.iterrows():
                sample_key = str(row['sample_key'])
                model_name = str(row['model_name'])
                processed_samples.add((sample_key, model_name))
            logger.info(f"Detected processed samples: {len(processed_samples)}")
        except Exception as e:
            logger.warning(f"Failed to read processed samples file: {e}")

    return processed_samples


def main():
    """Main function, supports checkpoint resume"""
    logger.info("=" * 60)
    logger.info("Starting automated evaluation")
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Load data
    df = load_evaluation_data()
    total_samples = len(df)

    # Load processed samples
    processed_samples = load_processed_samples(filename='evaluated0.csv')

    # Filter out unprocessed samples
    if processed_samples:
        # Create identifier column for filtering, convert to string type uniformly
        df['sample_id'] = df.apply(lambda row: (str(row['sample_key']), str(row['model_name'])), axis=1)
        # Filter out unprocessed samples
        df_unprocessed = df[~df['sample_id'].isin(processed_samples)].copy()
        # Delete temporary column
        df_unprocessed = df_unprocessed.drop(columns=['sample_id'])

        skipped_count = len(df) - len(df_unprocessed)
        logger.info(f"Skipped processed samples: {skipped_count}")
        logger.info(f"Samples to process: {len(df_unprocessed)}")

        if len(df_unprocessed) == 0:
            logger.info("All samples processed!")
            df = pd.DataFrame()  # Empty DataFrame
        else:
            df = df_unprocessed
    else:
        logger.info(f"Samples to process: {total_samples}")

    # If no samples to process, display existing results statistics
    if len(df) == 0:
        logger.info("No samples to process, displaying existing results statistics...")
        # Load complete results and display statistics
        output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation_results', 'evaluated0.csv')
        if os.path.exists(output_path):
            final_df = pd.read_csv(output_path)
            show_statistics(final_df)
        return

    # Store all results
    all_results = []
    batch_size = 50
    processed_count = 0
    remaining_samples = len(df)

    # Set max thread count
    max_workers = min(8, os.cpu_count() or 1)
    logger.info(f"Using {max_workers} threads for parallel processing")

    # Prepare sample data
    sample_data = [(idx, row) for idx, row in df.iterrows()]

    # Use thread pool for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_idx = {}
        for idx, row in sample_data:
            future = executor.submit(process_single_sample, (idx, row))
            future_to_idx[future] = idx

        # Process completed tasks
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]

            try:
                result = future.result()
                all_results.append(result)
                processed_count += 1

                # Stream progress output
                logger.info(f"Progress: {processed_count}/{remaining_samples} - sample {result['sample_key']} - {result['model_name']} - completed")

                # Save every 50 processed samples
                if len(all_results) >= batch_size:
                    save_batch_results(all_results, is_final=False, filename='evaluated0.csv')
                    all_results = []

            except Exception as e:
                logger.error(f"Task execution failed: sample index {idx}, error: {e}")

    # Save remaining results
    if all_results:
        save_batch_results(all_results, is_final=True, filename='evaluated0.csv')

    # Load complete results and display statistics
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'evaluation_results', 'evaluated0.csv')
    if os.path.exists(output_path):
        final_df = pd.read_csv(output_path)
        show_statistics(final_df)


if __name__ == "__main__":
    main()