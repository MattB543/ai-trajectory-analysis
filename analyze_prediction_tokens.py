# Script to analyze token usage in prediction extractions
from pathlib import Path
import json

output_dir = Path('outputs/extract_predictions_v2')
full_result_files = list(output_dir.glob('*_full_result_*.json'))

print('Analyzing token usage in prediction extractions...\n')
print('='*80)

results = []
for f in sorted(full_result_files):
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            usage = data.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            doc_title = data.get('document_title', 'Unknown')[:60]

            # Truncated test docs would have very low input tokens (around 1000 or less)
            is_truncated = input_tokens < 2000

            results.append({
                'file': f.name,
                'title': doc_title,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'truncated': is_truncated
            })
    except Exception as e:
        print(f'Error reading {f.name}: {e}')

# Sort by input tokens
results.sort(key=lambda x: x['input_tokens'])

print(f'Total files analyzed: {len(results)}\n')

truncated_count = sum(1 for r in results if r['truncated'])
full_count = len(results) - truncated_count

print(f'Truncated (< 2000 tokens): {truncated_count}')
print(f'Full documents: {full_count}\n')

print('='*80)
print('All extractions sorted by input tokens:\n')

for i, r in enumerate(results, 1):
    flag = '[TRUNCATED]' if r['truncated'] else '[FULL]'
    print(f'{i:2}. {flag:12} | In: {r["input_tokens"]:6,} | Out: {r["output_tokens"]:6,} | {r["title"]}')

print('\n' + '='*80)
print(f'\nSUMMARY:')
print(f'  Total extractions: {len(results)}')
print(f'  Truncated tests: {truncated_count}')
print(f'  Full documents: {full_count}')

if full_count > 0:
    avg_input = sum(r['input_tokens'] for r in results if not r['truncated']) / full_count
    avg_output = sum(r['output_tokens'] for r in results if not r['truncated']) / full_count
    print(f'\n  Average tokens for FULL docs:')
    print(f'    Input: {avg_input:,.0f}')
    print(f'    Output: {avg_output:,.0f}')
