# DSİ Streamflow Full Reader (Smart Row Scan System)

A robust Python script to extract comprehensive hydrological station data from DSİ annual streamflow report PDFs (2000-2020) using an intelligent line-by-line scanning method.

## 🎯 Features

- **Smart Row Scan System**: Implements line-by-line scanning to accurately detect and extract station data
- **Target Station Filtering**: Automatically detects and extracts only specified target stations
- **Comprehensive Data Extraction**: Extracts header info, monthly flow tables, and annual summaries
- **Duplicate Prevention**: Avoids processing duplicate station-year combinations
- **Progress Logging**: Detailed console and file logging with progress tracking
- **CSV Output**: Structured CSV output with all extracted data

## 📋 Target Stations

The script automatically detects and extracts data for these specific stations:

```
D14A011, D14A117, D14A144, D14A146, D14A149, D14A162,
D14A172, D14A192, D14A018, D22A093, D22A095, D22A105,
D22A106, D22A158, E22A054, D22A116, E22A065
```

## 🏗️ Installation

1. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Required Libraries**:
   - `pdfplumber>=0.9.0` - For PDF text extraction
   - `pandas>=1.5.0` - For data manipulation
   - `PyMuPDF>=1.23.0` - For PDF processing (alternative)
   - `pathlib2>=2.3.7` - For path handling

## 🚀 Usage

### Basic Usage

```python
from dsi_streamflow_full_reader import DSIStreamflowFullReader

# Initialize the reader
pdf_directory = r"C:\Users\Asus\Desktop\bitirme_projesi\debi_raporlari\akim_gözlem_yilligi"
output_csv = r"C:\Users\Asus\Desktop\bitirme_projesi\outputs\dsi_2000_2020_rowwise_extracted.csv"

reader = DSIStreamflowFullReader(pdf_directory, output_csv)

# Process all PDFs
results = reader.process_all_pdfs()
```

### Command Line Usage

```bash
python dsi_streamflow_full_reader.py
```

### Test the Implementation

```bash
python test_dsi_reader.py
```

## 📊 Output Format

The script generates a comprehensive CSV file with the following structure:

### Header Information
- `file`: PDF filename
- `year`: Extracted year from filename
- `station_code`: Station code (e.g., D14A011)
- `station_name`: Station name
- `coordinates`: Geographic coordinates
- `catchment_area_km2`: Catchment area in km²
- `annual_avg_flow_m3s`: Annual average flow in m³/s

### Monthly Flow Data
For each month (Ekim, Kasım, Aralık, Ocak, Şubat, Mart, Nisan, Mayıs, Haziran, Temmuz, Ağustos, Eylül):

- `{month}_flow_max_m3`: Maximum flow
- `{month}_flow_min_m3`: Minimum flow  
- `{month}_flow_avg_m3`: Average flow
- `{month}_ltsnkm2`: LT/SN/Km² values
- `{month}_akim_mm`: AKIM mm values
- `{month}_milm3`: MIL. M3 values

### Annual Summary
- `annual_total_m3`: Annual total flow
- `mm_total`: Total mm
- `avg_ltsnkm2`: Average LT/SN/Km²

## 🔍 Extraction Logic

### 1. PDF Processing
- Loops through all PDF files in the specified directory
- Extracts year from filename (e.g., `dsi_2010.pdf` → `2010`)

### 2. Page Scanning
- Scans each page line by line
- Checks line 2 for target station codes
- Skips pages that don't contain target stations

### 3. Header Extraction
- **Station Code**: Extracted from line 2
- **Station Name**: Text after station code on line 2
- **Coordinates**: Line 5 coordinate information
- **Catchment Area**: Line containing "YAĞIŞ ALANI"
- **Annual Average Flow**: Line containing "Su Yılında"

### 4. Flow Table Extraction
- Locates flow tables starting around line 58
- Extracts data for each row type:
  - Maks. (Maximum values)
  - Min. (Minimum values)
  - Ortalama (Average values)
  - LT/SN/Km2 values
  - AKIM mm. values
  - MİL. M3 values

### 5. Footer Extraction
- Finds data below double line (====)
- Extracts annual totals and summary statistics

## 📝 Logging

The script provides comprehensive logging:

- **Console Output**: Real-time progress updates
- **Log File**: Detailed logs saved to `dsi_extraction.log`
- **Progress Messages**: Shows which stations are found and processed

Example log output:
```
✅ D14A011 found in dsi_2005.pdf page 247
✅ D22A106 found in dsi_2012.pdf page 593
⚠️ Skipped: not target station
```

## 🛠️ Configuration

### Target Stations
To modify target stations, edit the `target_stations` set in the `DSIStreamflowFullReader` class:

```python
self.target_stations = {
    'D14A011', 'D14A117', 'D14A144', # ... add your stations
}
```

### Output Path
Modify the output CSV path in the constructor or main function:

```python
output_csv = r"your\custom\path\output.csv"
```

### PDF Directory
Update the PDF directory path:

```python
pdf_directory = r"your\pdf\directory\path"
```

## 🔧 Troubleshooting

### Common Issues

1. **PDF Directory Not Found**
   - Verify the PDF directory path exists
   - Ensure PDF files are present in the directory

2. **No Stations Found**
   - Check that target station codes are correct
   - Verify PDF files contain the expected station data

3. **Memory Issues**
   - The script processes one PDF at a time to minimize memory usage
   - Consider processing smaller batches if memory is limited

4. **Encoding Issues**
   - The script uses UTF-8 encoding for all text processing
   - Ensure your system supports UTF-8

### Performance Tips

- The script is optimized for speed using pdfplumber
- Processing time depends on the number and size of PDF files
- Progress is logged continuously for monitoring

## 📈 Example Output

```csv
Showing the first few rows of extracted data:

file,year,station_code,station_name,coordinates,catchment_area_km2,annual_avg_flow_m3s,ekim_flow_max_m3,kasim_flow_max_m3,...,annual_total_m3,mm_total,avg_ltsnkm2
dsi_2020.pdf,2020,E03A016,"Simav Ç. Yahyaköy","28°10'34''D, 39°59'10''K",6454,14.596,7.58,8.35,...,5.64,18.37,193,6.1
dsi_2019.pdf,2019,D14A011,"Station Name","27°56'33''D, 38°29'36''K",95,0.581,0.45,0.52,...,0.38,15.2,160,6.1
```

## 🤝 Contributing

To extend or modify the script:

1. Follow the existing code structure
2. Add comprehensive error handling
3. Update logging for new features
4. Test with sample PDF files
5. Update documentation

## 📄 License

This script is provided as-is for educational and research purposes.

## 🆘 Support

For issues or questions:
1. Check the log files for detailed error messages
2. Verify PDF file format and content
3. Ensure all dependencies are properly installed
4. Test with the provided test script first
