from cx_Freeze import setup, Executable

# Define the base options for the setup
options = {
    "build_exe": {
        "include_files": ["sf_creds.json", "sf_query.py"],
        "packages": ["os", "sys", "json", "pickle", "dateutil"],  # Add the package names here
        "includes": ["csv", "ctypes", "re", "time"],  # List any additional modules you want to include
    }
}

# List of executables
executables = [
    Executable(
        r"C:\Users\Bryan Edman\Documents\AMUncontacted\main.py",  # Replace with the name of your main script
        #targetName="UncontactedCSVCreator.exe",  # Name of the generated executable
    )
]


# Setup the project
setup(
    name="UncontactedCSVCreator",
    version="1.1",
    description="SDR/AM tool to check for converted and uncontacted Accounts in Salesforce and generate a CSV file for each agent.",
    options=options,
    executables=executables
)