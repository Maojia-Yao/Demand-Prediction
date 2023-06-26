1.
Install python3.6 or above version

2.
Can be done or not (create a python3 virtual directory to isolate the mutual influence between different version libraries)

3. 
requirements.txt contains all the libraries that need to be installed to run the program. The choice of the specific version number of the library depends on the version of python you have installed. Enter the project directory under the terminal and execute:
pip3 install --upgrade -r requirements.txt or (pip install --upgrade -r requirements.txt)

4.
Execute under the terminal:
jupyter notebook predict_model.ipynb

5.
If you want to run the code of predict_model.ipynb in Jupyter, you must download and deploy Pyspark, Scala, Java and Hadoop on the local computer (ioperating system). However, Jupyter has cached the results of running the code, so you don't have to run the code yourself.

6.
Open another terminal to execute:
python3 app.py or (python app.py)

7.
Open the browser and access the following URL:
http://localhost:5000/home

8.
You can register and log in on the homepage to use the website.

9.
You can also log in directly with the following administrator account and password:
username: admin@gmail.com
password: admin

10.
If it is the first time you click the "ML_colab" button connected to the Jupyter interface on the homepage of the web application in the computer, you may need to enter the token. You can find the token in the console output from when you started the Jupyter notebook server. The token is a string of characters that appears at the end of the URL that the Jupyter notebook server printed when it started up.