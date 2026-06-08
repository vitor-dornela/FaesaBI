import pandas as pd
import warnings
import csv
import io
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

def get_metrics(filepath):
    w_list = []
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        pd.read_csv(filepath, engine='python', on_bad_lines='warn', encoding='latin1')
        w_list = [str(warn.message) for warn in w if issubclass(warn.category, pd.errors.ParserWarning)]
    
    linhas_afetadas = []
    for msg in w_list:
        match = re.search(r'line (\d+)', msg)
        if match:
            linhas_afetadas.append(int(match.group(1)))
            
    # now clean
    cleaned_rows = []
    with open(filepath, 'r', encoding='latin1') as f:
        reader = csv.reader(f)
        header = next(reader)
        current_row = []
        for row in reader:
            if not current_row:
                if not row: continue
                current_row = row
            else:
                if not row:
                    current_row[-1] += '\n'
                else:
                    current_row[-1] = current_row[-1] + '\n' + row[0]
                    current_row.extend(row[1:])
            if len(current_row) < 34: continue
            if len(current_row) > 34:
                excess = len(current_row) - 34
                desc_pieces = current_row[32:33+excess]
                desc = ','.join(desc_pieces).replace('"', "'")
                current_row = current_row[:32] + [desc] + [current_row[-1]]
            cleaned_rows.append(current_row)
            current_row = []
            
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    writer.writerows(cleaned_rows)
    output.seek(0)
    
    w_list_after = []
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        pd.read_csv(output, engine='python', on_bad_lines='warn')
        w_list_after = [str(warn.message) for warn in w if issubclass(warn.category, pd.errors.ParserWarning)]
        
    return len(linhas_afetadas), len(w_list_after), len(cleaned_rows)

m_2016 = get_metrics('despesas_vitoria_2016_P.csv')
m_2026 = get_metrics('despesas_vitoria_2026_P.csv')

print(f'2016: Bad lines before={m_2016[0]}, Bad lines after={m_2016[1]}, Total Clean Rows={m_2016[2]}')
print(f'2026: Bad lines before={m_2026[0]}, Bad lines after={m_2026[1]}, Total Clean Rows={m_2026[2]}')
