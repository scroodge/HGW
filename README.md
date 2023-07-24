# HGW
Python script to get route list from Haivision Gateway

INSTALLATION
1. Create Python vnev to execute scrip => python -m venv .venv 
2. Check => pip list  
3. Install pip modules => pip install -r requirements.txt
4. Download Prometheus version https://prometheus.io/download/ and install it (Windows version in my case)
5. Open prometheus.yaml and Enter YOUR - job_name, static_configs.
6. Run prometheus.exe. 
6. Setup Your DB to get data from Your prometheus Server.
7. Run main.py and choose Source to monitor if available.
