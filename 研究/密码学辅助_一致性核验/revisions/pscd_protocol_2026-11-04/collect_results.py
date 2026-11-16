"""Reconcile every planned cell from immutable per-attempt result files."""
from collections import Counter
from pathlib import Path
import csv
import argparse
import json
import statistics
from public_models import ROOT,save_json


def collect(directory):
    directory=Path(directory)
    plan=json.loads((directory/'PLAN.json').read_text())
    rows=[];attempts=[]
    for cell in plan['cells']:
        paths=sorted((directory/'runs'/cell['id']).glob('attempt*/result.json'))
        records=[]
        for path in paths:
            try:record=json.loads(path.read_text())
            except json.JSONDecodeError:continue
            record['result_file']=str(path.relative_to(ROOT));records.append(record);attempts.append(record)
        latest=records[-1] if records else {}
        row={**cell,'status':latest.get('status','NOT_RUN'),'attempt_count':len(records),
             'result_file':latest.get('result_file'),**latest.get('metrics',{}),**latest.get('prepare_metrics',{})}
        row['runtime_wall_seconds']=latest.get('runtime_wall_seconds')
        row['output_field_elements']=latest.get('verification',{}).get('output_field_elements')
        row['compile_source_hashes']=latest.get('compile',{}).get('source_hashes')
        rows.append(row)
    groups=[]
    metric_names=['triples_consumed','global_data_sent_MB','online_rounds','offline_rounds','party0_total_rounds',
                  'reported_seconds','online_seconds','offline_seconds','matrix_field_elements','coordinate_field_elements',
                  'pad_field_elements','protocol_random_bits_drawn','prepare_ns','output_field_elements']
    for profile in ['P0','P1','P2']:
        for n in [8,64,256]:
            for method in ['pscd','coordinate_nonzero','private_zero','full_shared_reference','pad_only']:
                selected=[row for row in rows if (row['profile'],row['n'],row['method'])==(profile,n,method)]
                successful=[row for row in selected if row['status']=='PASS']
                entry={'profile':profile,'n':n,'method':method,'planned':len(selected),'passes':len(successful),
                       'status_counts':dict(Counter(row['status'] for row in selected))}
                for key in metric_names:
                    values=[row[key] for row in successful if row.get(key) is not None]
                    entry[key+'_mean']=statistics.mean(values) if values else None
                    entry[key+'_range']=[min(values),max(values)] if values else None
                    entry[key+'_observed_count']=len(values)
                groups.append(entry)
    statuses=dict(Counter(row['status'] for row in rows))
    result={'planned_cells':135,'statuses':statuses,'attempts_recorded':len(attempts),
            'collection_source':'all per-attempt result files, including records after the first reporter stopped',
            'rows':rows,'groups':groups,'all_terminal':all(row['status'] not in ('NOT_RUN','STARTED') for row in rows)}
    save_json(directory/'RESULTS.json',result)
    with (directory/'RECOVERED_ATTEMPTS.jsonl').open('w') as stream:
        for item in attempts:stream.write(json.dumps(item,ensure_ascii=False)+'\n')
    fields=['id','profile','n','repeat','method','status','attempt_count','result_file']+metric_names
    with (directory/'MEASUREMENTS.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--directory',default='evaluation_final');args=parser.parse_args()
    result=collect(ROOT/args.directory);print(json.dumps({key:result[key] for key in ['planned_cells','statuses','attempts_recorded','all_terminal']}))
