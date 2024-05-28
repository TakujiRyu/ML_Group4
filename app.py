from flask import Flask, request, render_template, jsonify
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Load the model
try:
    model = pickle.load(open('pipe.pkl', 'rb'))
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return render_template('index.html', prediction_text='Model not available.')
    
    if request.method == 'POST':
        try:
            company = request.form['company']
            type_name = request.form['type_name']
            ram = int(request.form['ram'])
            weight = float(request.form['weight'])
            touchscreen = 1 if request.form['touchscreen'] == 'Yes' else 0
            ips = 1 if request.form['ips'] == 'Yes' else 0
            ppi = float(request.form['ppi'])
            cpu_brand = request.form['cpu_brand']
            hdd = int(request.form['hdd'])
            ssd = int(request.form['ssd'])
            gpu_brand = request.form['gpu_brand']
            os = request.form['os']
            
            # Create the input array for the model
            input_data = pd.DataFrame([[company, type_name, ram, weight, touchscreen, ips, ppi, cpu_brand, hdd, ssd, gpu_brand, os]], 
                                    columns=['Company', 'TypeName', 'Ram', 'Weight', 'Touchscreen', 'Ips', 'ppi', 'Cpu brand', 'HDD', 'SSD', 'Gpu brand', 'os'])
            
            # Predict the price
            prediction = model.predict(input_data)[0]
            predicted_price = np.exp(prediction)  # Remember, the target variable was log-transformed
            
            # Generate random actual prices for demonstration
            actual_prices = np.random.normal(predicted_price, 200, 10)
            
            # Create the graph
            plt.figure(figsize=(10, 5))
            plt.plot(actual_prices, label='Actual Prices', marker='o')
            plt.axhline(y=predicted_price, color='r', linestyle='-', label='Predicted Price')
            plt.xlabel('Sample Index')
            plt.ylabel('Price')
            plt.title('Predicted Price vs Actual Prices')
            plt.legend()
            graph_path = 'static/prediction_graph.png'
            plt.savefig(graph_path)
            plt.close()
            
            return render_template('result.html', prediction_text=f'Predicted Laptop Price: ${predicted_price:.2f}', graph_path=graph_path)
        
        except Exception as e:
            return render_template('index.html', prediction_text=f'Error in prediction: {e}')

@app.route('/delete_graph', methods=['GET'])
def delete_graph():
    graph_path = 'static/prediction_graph.png'
    if os.path.exists(graph_path):
        os.remove(graph_path)
        return jsonify({'message': 'Graph deleted successfully'})
    else:
        return jsonify({'message': 'Graph not found'})

if __name__ == '__main__':
    # Change the host to '0.0.0.0' and the port to 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
