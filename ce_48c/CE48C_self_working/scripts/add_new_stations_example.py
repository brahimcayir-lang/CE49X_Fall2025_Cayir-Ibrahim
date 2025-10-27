#!/usr/bin/env python3
"""
Example script showing how to add new stations to the extraction process
"""

from extract_dsi_with_new_stations import DSIExtractorComplete

def extract_new_stations():
    """Example of how to add new stations and extract data."""
    
    # Define your new stations
    # Add the station codes you want to extract
    new_stations = {
        # Existing stations
        'D22A144', 'D22A145', 'D22A065', 'D22A093', 
        'D22A095', 'D14A149', 'D22A158',
        
        # New stations you want to add
        'D14A162',  # Yeşilırmak Kozlu
        'D22A105',  # Değirmen Deresi Salipazarı
        'D22A192',  # Kelkit N
        'D22A172',  # Kelkit Ç
        
        # Add more stations here as needed:
        # 'D22A200', 'D22A201', 'D22A202'
    }
    
    # Configuration
    PDF_DIRECTORY = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
    OUTPUT_CSV = "dsi_data_with_new_stations.csv"
    
    print(f"Extracting data for {len(new_stations)} stations:")
    for station in sorted(new_stations):
        print(f"  - {station}")
    
    # Create extractor and run
    extractor = DSIExtractorComplete(PDF_DIRECTORY, OUTPUT_CSV, new_stations)
    extractor.run()
    
    print(f"\nExtraction complete! Check the output file: {OUTPUT_CSV}")

if __name__ == "__main__":
    extract_new_stations()
