import pandas as pd
import numpy as np

def analyze_ccts_data():
    """Analyze CCTS regulatory complaint data for key insights"""
    
    # Read CCTS data with different encodings
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
            try:
                # Skip header rows and use proper column names
                df = pd.read_csv('/Users/amirshayegh/Developer/temp/review_analysis/Data/CCTS.csv', 
                               encoding=encoding, skiprows=6)
                print(f"Successfully read with encoding: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise Exception("Could not decode file with any common encoding")
            
        print(f"CCTS Data Analysis")
        print(f"=" * 50)
        print(f"Total complaints: {len(df):,}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nSample data:")
        print(df.head())
        
        # Clean up and analyze the data
        # Look for issue type columns
        for col in df.columns:
            if 'issue' in col.lower() or 'category' in col.lower() or 'type' in col.lower():
                print(f"\nFound potential category column: {col}")
                if not df[col].isna().all():
                    print(f"Value counts for {col}:")
                    print(df[col].value_counts().head(10))
                    
        # Look for billing-related patterns
        billing_keywords = ['billing', 'bill', 'charge', 'payment', 'fee', 'cost']
        service_keywords = ['service', 'quality', 'outage', 'disconnect', 'installation']
        network_keywords = ['network', 'coverage', 'signal', 'connectivity', 'internet']
        
        # Analyze text content in all columns
        for col in df.columns:
            if df[col].dtype == 'object':
                combined_text = df[col].astype(str).str.lower().str.cat(sep=' ')
                
                billing_count = sum(combined_text.count(kw) for kw in billing_keywords)
                service_count = sum(combined_text.count(kw) for kw in service_keywords)
                network_count = sum(combined_text.count(kw) for kw in network_keywords)
                
                if billing_count > 0 or service_count > 0 or network_count > 0:
                    print(f"\nKeyword analysis for column '{col}':")
                    print(f"  Billing-related: {billing_count} mentions")
                    print(f"  Service-related: {service_count} mentions")
                    print(f"  Network-related: {network_count} mentions")
                    
    except Exception as e:
        print(f"Error reading CCTS data: {e}")
        return

if __name__ == "__main__":
    analyze_ccts_data()