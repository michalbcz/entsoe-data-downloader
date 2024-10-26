import glob
import zipfile

# List all CSV files in the directory
csv_files = glob.glob('data/*.csv')

# Step 1: Combine CSV files into a single file
combined_file = 'combined.csv'
with open(combined_file, 'w') as outfile:
    header_written = False
    for file in csv_files:
        with open(file, 'r') as infile:
            # Read the first line (header)
            header = infile.readline()
            # Write the header only once (from the first file)
            if not header_written:
                outfile.write(header)
                header_written = True
            # Write the rest of the file, skipping any headers
            outfile.write(infile.read())

# Step 2: Zip the combined CSV file
zip_filename = 'combined.zip'
with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(combined_file)

print(f"Combined CSV file created and zipped as '{zip_filename}'")