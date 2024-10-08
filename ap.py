from flask import Flask, render_template, request
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Usar el backend no interactivo
import matplotlib.pyplot as plt
import sympy as sp
import re
import io
import base64

app = Flask(__name__)

# Función para limpiar y convertir la entrada del usuario
def parse_function(user_input):
    user_input = user_input.replace('^', '**')  # Reemplazar ^ con **
    user_input = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', user_input)  # Insertar multiplicación
    return sp.sympify(user_input)

# Función para calcular el polinomio de Taylor
def taylor_series(func, point, degree):
    x = sp.symbols('x')
    taylor_poly = func.series(x, point, n=degree + 1).removeO()
    return taylor_poly

# Función para graficar la función y su polinomio de Taylor
def plot_function_and_taylor(func, point, degree):
    x = sp.symbols('x')

    # Convertir la función a una que entienda numpy
    func_sym = sp.lambdify(x, func, 'numpy')
    x_vals = np.linspace(point - 5, point + 5, 400)
    y_vals = func_sym(x_vals)

    # Calcula el polinomio de Taylor
    taylor_poly = taylor_series(func, point, degree)
    taylor_poly_sym = sp.lambdify(x, taylor_poly, 'numpy')
    taylor_y_vals = taylor_poly_sym(x_vals)

    # Crear la gráfica
    plt.figure(figsize=(10, 8))
    plt.plot(x_vals, y_vals, label='Función Original', color='black', linewidth=2)
    plt.plot(x_vals, taylor_y_vals, label=f'Polinomio de Taylor (Grado {degree})', linestyle='--', color='blue', linewidth=2)
    plt.axvline(x=point, color='red', linestyle='--', label='Punto de Ajuste')
    plt.title('Ajuste de Taylor', fontsize=16, fontweight='bold')
    plt.xlabel('x', fontsize=14)
    plt.ylabel('y', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='-.')
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Guardar la gráfica en memoria
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return plot_url

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        func_input = request.form['func']
        degree_input = int(request.form['degree'])
        point_input = float(request.form['point'])

        # Parsear y graficar
        func = parse_function(func_input)
        plot_url = plot_function_and_taylor(func, point_input, degree_input)
        return render_template('index.html', plot_url=plot_url)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
