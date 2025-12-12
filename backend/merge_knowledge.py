import pandas as pd
import os

def merge_knowledge():
    # Load existing CSVs
    files = ['agriculture_knowledge.csv', 'agriculture_knowledge_pro.csv']
    dfs = []
    
    for f in files:
        if os.path.exists(f):
            try:
                df = pd.read_csv(f)
                # Standardize columns
                # Pro has 'Intent', 'Topic', 'Question', 'Answer'
                # Basic has 'Topic', 'Question', 'Answer'
                if 'Intent' not in df.columns:
                    df['Intent'] = 'general' # Default intent
                
                # Ensure column order
                df = df[['Intent', 'Topic', 'Question', 'Answer']]
                dfs.append(df)
                print(f"Loaded {len(df)} rows from {f}")
            except Exception as e:
                print(f"Error loading {f}: {e}")
    
    if dfs:
        # Merge
        merged_df = pd.concat(dfs, ignore_index=True)
        
        # Remove duplicates based on Question
        before = len(merged_df)
        merged_df.drop_duplicates(subset=['Question'], keep='last', inplace=True)
        after = len(merged_df)
        print(f"Merged {before} rows -> {after} unique rows.")
        
        # Save
        merged_df.to_csv('unified_knowledge_base.csv', index=False)
        print("Saved to unified_knowledge_base.csv")
    else:
        print("No data found to merge.")

if __name__ == "__main__":
    merge_knowledge()
