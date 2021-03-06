# Parallel-Image-Processing

Group Project for Distrubuted Systems and Cloud Computing. 

Dependencies for Execution
1. [The models git repo for TensorFlow](https://github.com/tensorflow/models) needs to be pulled into every worker and ps node in your system. It should be pulled into the same folder as the *test_ps.py* and *test_worker.py* files (located in *server/googlenet* and *node_code* repestively).
2. Python 3.5.3.
3. A virtual environment with TensorFlow, Paramiko, netifaces installed. See [here](https://virtualenv.pypa.io/en/latest/) for more details on installing and using virtualenv.

Instructions for Execution
1. Run *python default_discovery.py* in the *discovery* folder if you are using your own LAN with Pis connected to deploy code to all the Pis on your network. 
2. Run *python -m http.server* in the *client* folder to start an HTTP server on the machine you intend to use an PS in tensorflow. 
3. Run *python server.py* in the *server* folder to start the Flask server that will send requests to TensorFlow
4. Run *python test_worker.py* in */home/pi/cloud_computing/Parallel-Image-Processing/node_code/* on each of your Pis
5. Load the webpage in *client/index.html* and upload your image, probabilities of what the image is should appear on the screen.
