import pandas as pd
import json

def load_findsum_data(csv_path, text_path, num_rows=10):
    # Load CSV file
    df = pd.read_csv(csv_path, sep=',', nrows=num_rows)
    
    # Load text file
    with open(text_path, 'r', encoding='utf-8') as f:
        text_data = [json.loads(line) for _, line in zip(range(num_rows), f)]
    
    return df, text_data

def extract_important_metrics(data):
    # Initialize a dictionary to store the extracted metrics
    metrics = {}

    # Helper function to safely extract float values
    def safe_float(value):
        try:
            # Handle cases where the value contains '&' or commas
            if '&' in value:
                return float(value.split('&')[1].replace(',', ''))
            else:
                return float(value.replace(',', ''))
        except (ValueError, IndexError):
            return None

    # Extract liquidity-related metrics
    if 'mda_liquidity_tables' in data[0]:
        liquidity_data = data[0]['mda_liquidity_tables'][0]
        for item in liquidity_data:
            if 'total identifiable intangible assets' in item[0].lower():
                metrics['total_identifiable_intangible_assets'] = safe_float(item[2])
            elif 'trade names' in item[0].lower():
                metrics['trade_names'] = safe_float(item[2])
            elif 'developed technology' in item[0].lower():
                metrics['developed_technology'] = safe_float(item[2])
            elif 'customer relationships' in item[0].lower():
                metrics['customer_relationships'] = safe_float(item[2])

    # Extract balance sheet metrics
    if 'after_mda_tables' in data[0]:
        balance_sheet_data = data[0]['after_mda_tables'][0]
        for item in balance_sheet_data:
            if 'total current assets' in item[0].lower():
                metrics['current_assets'] = safe_float(item[2])
            elif 'total assets' in item[0].lower():
                metrics['total_assets'] = safe_float(item[2])
            elif 'total current liabilities' in item[0].lower():
                metrics['current_liabilities'] = safe_float(item[2])
            elif 'total liabilities' in item[0].lower():
                metrics['total_liabilities'] = safe_float(item[2])
            elif 'total stockholders equity' in item[0].lower():
                metrics['total_stockholders_equity'] = safe_float(item[2])
            elif 'cash and cash equivalents' in item[0].lower():
                metrics['cash_and_cash_equivalents'] = safe_float(item[2])
            elif 'inventories' in item[0].lower():
                metrics['inventory'] = safe_float(item[2])
            elif 'accounts receivable' in item[0].lower():
                metrics['accounts_receivable'] = safe_float(item[2])
            elif 'accounts payable' in item[0].lower():
                metrics['accounts_payable'] = safe_float(item[2])
            elif 'goodwill' in item[0].lower():
                metrics['goodwill'] = safe_float(item[2])
            elif 'intangible assets net' in item[0].lower():
                metrics['intangible_assets'] = safe_float(item[2])
            elif 'long-term debt net of current portion' in item[0].lower():
                metrics['long_term_debt'] = safe_float(item[2])

    # Extract income statement metrics
    if 'after_mda_tables' in data[0]:
        income_statement_data = data[0]['after_mda_tables'][1]
        for item in income_statement_data:
            if 'sales' in item[0].lower():
                metrics['sales'] = safe_float(item[2])
            elif 'net earnings' in item[0].lower():
                metrics['net_earnings'] = safe_float(item[2])
            elif 'basic net earnings per common share' in item[0].lower():
                metrics['basic_eps'] = safe_float(item[2])
            elif 'diluted net earnings per common share' in item[0].lower():
                metrics['diluted_eps'] = safe_float(item[2])
            elif 'operating earnings' in item[0].lower():
                metrics['operating_earnings'] = safe_float(item[2])
            elif 'gross profit' in item[0].lower():
                metrics['gross_profit'] = safe_float(item[2])
            elif 'depreciation depletion and amortization' in item[0].lower():
                metrics['depreciation_and_amortization'] = safe_float(item[2])

    # Extract cash flow metrics
    if 'after_mda_tables' in data[0]:
        cash_flow_data = data[0]['after_mda_tables'][2]
        for item in cash_flow_data:
            if 'net cash provided by operating activities' in item[0].lower():
                metrics['net_cash_operating_activities'] = safe_float(item[2])
            elif 'net cash used in investing activities' in item[0].lower():
                metrics['net_cash_investing_activities'] = safe_float(item[2])
            elif 'net cash provided by financing activities' in item[0].lower():
                metrics['net_cash_financing_activities'] = safe_float(item[2])

    return metrics

def save_metrics_to_csv(df, text_data, output_path):
    metrics_list = [extract_important_metrics([data]) for data in text_data]
    metrics_df = pd.DataFrame(metrics_list)
    combined_df = pd.concat([df, metrics_df], axis=1)
    combined_df.to_csv(output_path, index=False)
    print(f"Metrics and data saved to {output_path}")

if __name__ == "__main__": 
    # Example usage
    csv_file_path = "text/FINDSum-Liquidity/liquidity_input_2000/train_liquidity_segment_2_input_2_1000.csv"
    text_file_path = "table/FINDSum-Liquidity/train_liquidity_all_tuples_diff_sec.txt"
    output_csv_path = "output.csv"

    df, text_data = load_findsum_data(csv_file_path, text_file_path, num_rows=10)
    save_metrics_to_csv(df, text_data, output_csv_path)
    # df, text_data = load_findsum_data(csv_file_path, text_file_path, num_rows=10)
    # # Display output
    # print("CSV Data:")
    # print(df.head())
    # print("\nText Data:")
    # print(text_data[:2])