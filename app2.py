"""
Application Flask pour AnimTrack - Solution de gestion d'élevage
Backend complet pour index2.html avec toutes les fonctionnalités
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os
import math
import re
from datetime import datetime, timedelta
from io import BytesIO
import csv

app = Flask(__name__)
CORS(app)

# Configuration
DATA_FILE = 'animaux.json'
IMAGES_FOLDER = 'images'

# ================================================
# CONSTANTES
# ================================================

CODE_ESPECE = {
    'Bovin': 'B',
    'Ovin': 'O',
    'Caprin': 'C',
    'Porcin': 'P',
    'Volaille': 'V'
}

GESTATION = {
    'Bovin': 280,
    'Ovin': 150,
    'Caprin': 150,
    'Porcin': 114,
    'Volaille': 21
}

# ================================================
# FONCTIONS UTILITAIRES
# ================================================

def load_data():
    """Charge les données depuis le fichier JSON"""
    if not os.path.exists(DATA_FILE):
        data = get_exemple_data()
        save_data(data)
        return data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return get_exemple_data()

def save_data(data):
    """Sauvegarde les données dans le fichier JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def calculate_imc(poids, taille):
    """Calcule l'IMC"""
    if poids and taille and taille > 0:
        return round(poids / ((taille / 100) ** 2), 1)
    return None

def generate_identifiant(espece):
    """Génère un identifiant unique par espèce (B001, C001, etc.)"""
    code = CODE_ESPECE.get(espece, 'X')
    animaux = load_data()
    
    existing_numbers = []
    for a in animaux:
        identifiant = a.get('identifiant', '')
        if identifiant and identifiant.startswith(code):
            match = re.search(rf'{code}(\d+)', identifiant)
            if match:
                existing_numbers.append(int(match.group(1)))
    
    existing_numbers.sort()
    next_num = 1
    for num in existing_numbers:
        if num == next_num:
            next_num += 1
        else:
            break
    
    return f"{code}{next_num:03d}"

def get_gestation_info():
    """Récupère les informations de gestation"""
    animaux = load_data()
    gestations = []
    today = datetime.now().date()
    
    for animal in animaux:
        if animal.get('sexe') == 'Femelle' and animal.get('derniere_reproduction'):
            try:
                derniere_repro = datetime.strptime(animal['derniere_reproduction'], '%Y-%m-%d').date()
                espece = animal.get('espece', 'Bovin')
                gestation_days = GESTATION.get(espece, 280)
                date_accouchement = derniere_repro + timedelta(days=gestation_days)
                jours_restants = (date_accouchement - today).days
                
                gestations.append({
                    'id': animal.get('id'),
                    'identifiant': animal.get('identifiant'),
                    'type': animal.get('type_animal', ''),
                    'espece': espece,
                    'race': animal.get('race', ''),
                    'date_accouchement': date_accouchement.strftime('%Y-%m-%d'),
                    'jours_restants': jours_restants,
                    'est_enceinte': jours_restants > 0 and jours_restants <= gestation_days,
                    'accouchement_aujourdhui': jours_restants == 0,
                    'accouchement_semaine': 0 <= jours_restants <= 7
                })
            except:
                pass
    
    return gestations

def get_exemple_data():
    """Données d'exemple"""
    return [
        {"id": 1, "identifiant": "B001", "type_animal": "Vache laitière", "age": 36, "sexe": "Femelle",
         "espece": "Bovin", "race": "Prim'Holstein", "poids": 720, "taille": 148, "imc": 328.7,
         "production_lait": 32.5, "conso_aliment": 21.0, "gmq": 780, "pathologies": "Aucune",
         "derniere_reproduction": "2024-06-15", "date_enregistrement": "2024-01-10T10:30:00Z"},
        {"id": 2, "identifiant": "B002", "type_animal": "Taureau", "age": 52, "sexe": "Mâle",
         "espece": "Bovin", "race": "Limousine", "poids": 950, "taille": 155, "imc": 395.5,
         "production_lait": 0, "conso_aliment": 24.5, "gmq": 890, "pathologies": "Aucune",
         "derniere_reproduction": None, "date_enregistrement": "2024-01-12T14:20:00Z"},
        {"id": 3, "identifiant": "C001", "type_animal": "Chèvre", "age": 36, "sexe": "Femelle",
         "espece": "Caprin", "race": "Alpine", "poids": 68, "taille": 78, "imc": 111.7,
         "production_lait": 3.5, "conso_aliment": 2.6, "gmq": 125, "pathologies": "Aucune",
         "derniere_reproduction": "2024-08-20", "date_enregistrement": "2024-02-05T09:15:00Z"},
        {"id": 4, "identifiant": "O001", "type_animal": "Brebis", "age": 24, "sexe": "Femelle",
         "espece": "Ovin", "race": "Boulonnaise", "poids": 88, "taille": 74, "imc": 160.7,
         "production_lait": 1.8, "conso_aliment": 2.9, "gmq": 175, "pathologies": "Aucune",
         "derniere_reproduction": "2024-07-05", "date_enregistrement": "2024-02-18T11:45:00Z"},
        {"id": 5, "identifiant": "P001", "type_animal": "Truie", "age": 18, "sexe": "Femelle",
         "espece": "Porcin", "race": "Large White", "poids": 135, "taille": 86, "imc": 182.5,
         "production_lait": 0, "conso_aliment": 4.8, "gmq": 680, "pathologies": "Aucune",
         "derniere_reproduction": "2024-09-10", "date_enregistrement": "2024-03-02T13:20:00Z"},
        {"id": 6, "identifiant": "V001", "type_animal": "Poule pondeuse", "age": 12, "sexe": "Femelle",
         "espece": "Volaille", "race": "Leghorn", "poids": 2.5, "taille": 35, "imc": 20.4,
         "production_lait": 0, "conso_aliment": 0.12, "gmq": 15, "pathologies": "Aucune",
         "derniere_reproduction": None, "date_enregistrement": "2024-03-10T10:00:00Z"}
    ]

# ================================================
# ROUTES PRINCIPALES
# ================================================

@app.route('/')
def index():
    """Page d'accueil"""
    try:
        return send_file('index2.html')
    except FileNotFoundError:
        return "Fichier index2.html non trouvé", 404

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Sert les images"""
    try:
        return send_from_directory(IMAGES_FOLDER, filename)
    except:
        return "", 404

# ================================================
# API ANIMAUX
# ================================================

@app.route('/api/animaux', methods=['GET'])
def get_animaux():
    """Liste tous les animaux"""
    return jsonify(load_data())

@app.route('/api/animaux/<int:id>', methods=['GET'])
def get_animal(id):
    """Récupère un animal par ID"""
    animaux = load_data()
    animal = next((a for a in animaux if a.get('id') == id), None)
    if animal:
        return jsonify(animal)
    return jsonify({'error': 'Animal non trouvé'}), 404

@app.route('/api/animaux/gestations', methods=['GET'])
def get_gestations():
    """Informations de gestation"""
    gestations = get_gestation_info()
    espece_filter = request.args.get('espece', 'tous')
    
    if espece_filter != 'tous':
        gestations = [g for g in gestations if g['espece'] == espece_filter]
    
    return jsonify({
        'total_enceintes': len([g for g in gestations if g['est_enceinte']]),
        'accouchements_aujourdhui': len([g for g in gestations if g['accouchement_aujourdhui']]),
        'accouchements_semaine': len([g for g in gestations if g['accouchement_semaine']]),
        'gestations': gestations
    })

@app.route('/api/animaux', methods=['POST'])
def add_animal():
    """Ajoute un animal"""
    try:
        data = request.get_json()
        animaux = load_data()
        
        # Validation
        errors = []
        if not data.get('age') or int(data.get('age', 0)) < 0 or int(data.get('age', 0)) > 300:
            errors.append("Âge invalide (0-300 mois)")
        if not data.get('sexe') or data.get('sexe') not in ['Mâle', 'Femelle']:
            errors.append("Sexe invalide")
        if not data.get('espece') or data.get('espece') not in CODE_ESPECE:
            errors.append("Espèce invalide")
        if not data.get('type_animal') or not data.get('type_animal').strip():
            errors.append("Type requis")
        if not data.get('race') or not data.get('race').strip():
            errors.append("Race requise")
        if not data.get('poids') or float(data.get('poids', 0)) < 0.1 or float(data.get('poids', 0)) > 2000:
            errors.append("Poids invalide (0.1-2000 kg)")
        if not data.get('taille') or float(data.get('taille', 0)) < 10 or float(data.get('taille', 0)) > 250:
            errors.append("Hauteur invalide (10-250 cm)")
        
        if errors:
            return jsonify({'error': 'Erreurs de validation', 'details': errors}), 400
        
        new_id = max([a.get('id', 0) for a in animaux], default=0) + 1
        identifiant = generate_identifiant(data.get('espece'))
        imc = calculate_imc(float(data.get('poids')), float(data.get('taille')))
        
        new_animal = {
            'id': new_id,
            'identifiant': identifiant,
            'type_animal': data.get('type_animal').strip(),
            'age': int(data.get('age')),
            'sexe': data.get('sexe'),
            'espece': data.get('espece'),
            'race': data.get('race').strip(),
            'poids': float(data.get('poids')),
            'taille': float(data.get('taille')),
            'imc': imc,
            'production_lait': float(data.get('production_lait', 0)),
            'conso_aliment': float(data.get('conso_aliment', 0)),
            'gmq': float(data.get('gmq', 0)),
            'pathologies': data.get('pathologies', 'Aucune').strip() or 'Aucune',
            'derniere_reproduction': data.get('derniere_reproduction') if data.get('derniere_reproduction') else None,
            'date_enregistrement': datetime.now().isoformat()
        }
        
        animaux.append(new_animal)
        save_data(animaux)
        
        return jsonify({'message': 'Animal ajouté', 'id': new_id, 'identifiant': identifiant, 'imc': imc}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/animaux/<int:id>', methods=['PUT'])
def update_animal(id):
    """Met à jour un animal"""
    try:
        data = request.get_json()
        animaux = load_data()
        
        index = next((i for i, a in enumerate(animaux) if a.get('id') == id), None)
        if index is None:
            return jsonify({'error': 'Animal non trouvé'}), 404
        
        for key, value in data.items():
            if key not in ['id', 'identifiant']:
                if key in ['age', 'poids', 'taille', 'production_lait', 'conso_aliment', 'gmq']:
                    try:
                        animaux[index][key] = float(value) if '.' in str(value) else int(value)
                    except:
                        animaux[index][key] = value
                else:
                    animaux[index][key] = value
        
        if 'poids' in data or 'taille' in data:
            imc = calculate_imc(animaux[index].get('poids'), animaux[index].get('taille'))
            if imc:
                animaux[index]['imc'] = imc
        
        save_data(animaux)
        return jsonify({'message': 'Animal mis à jour'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/animaux/<int:id>', methods=['DELETE'])
def delete_animal(id):
    """Supprime un animal"""
    animaux = load_data()
    animaux = [a for a in animaux if a.get('id') != id]
    save_data(animaux)
    return jsonify({'message': 'Animal supprimé'})

# ================================================
# API STATISTIQUES
# ================================================

@app.route('/api/stats/descriptives', methods=['GET'])
def get_descriptive_stats():
    """Statistiques descriptives"""
    animaux = load_data()
    
    if not animaux:
        return jsonify({'total': 0})
    
    numeric_fields = ['age', 'poids', 'taille', 'imc', 'production_lait', 'conso_aliment', 'gmq']
    stats = {'total': len(animaux)}
    
    for field in numeric_fields:
        values = [a.get(field) for a in animaux if a.get(field) is not None and a.get(field) != 0]
        
        if values:
            n = len(values)
            mean_val = sum(values) / n
            variance = sum((x - mean_val) ** 2 for x in values) / n
            std_dev = math.sqrt(variance)
            
            stats[field] = {
                'count': n,
                'moyenne': round(mean_val, 2),
                'ecart_type': round(std_dev, 2),
                'minimum': min(values),
                'maximum': max(values)
            }
    
    return jsonify(stats)

@app.route('/api/correlation', methods=['GET'])
def get_correlation_matrix():
    """Matrice de corrélation"""
    animaux = load_data()
    
    if len(animaux) < 3:
        return jsonify({'error': 'Pas assez de données'})
    
    variables = ['age', 'poids', 'taille', 'imc', 'production_lait', 'conso_aliment', 'gmq']
    
    data = []
    for animal in animaux:
        row = []
        valid = True
        for var in variables:
            val = animal.get(var)
            if val is None or val == 0:
                valid = False
                break
            row.append(float(val))
        if valid:
            data.append(row)
    
    if len(data) < 3:
        return jsonify({'error': 'Pas assez de données complètes'})
    
    n = len(data)
    m = len(variables)
    means = [sum(row[j] for row in data) / n for j in range(m)]
    
    corr_matrix = [[0 for _ in range(m)] for _ in range(m)]
    
    for i in range(m):
        for j in range(m):
            if i == j:
                corr_matrix[i][j] = 1
            else:
                cov = sum((data[k][i] - means[i]) * (data[k][j] - means[j]) for k in range(n)) / (n - 1)
                std_i = math.sqrt(sum((data[k][i] - means[i])**2 for k in range(n)) / (n - 1))
                std_j = math.sqrt(sum((data[k][j] - means[j])**2 for k in range(n)) / (n - 1))
                corr_matrix[i][j] = round(cov / (std_i * std_j), 4) if std_i > 0 and std_j > 0 else 0
    
    return jsonify({'variables': variables, 'matrix': corr_matrix})

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export CSV"""
    animaux = load_data()
    
    if not animaux:
        return jsonify({'error': 'Aucune donnée'}), 404
    
    output = BytesIO()
    writer = csv.writer(output)
    
    headers = ['id', 'identifiant', 'type_animal', 'age', 'sexe', 'espece', 'race', 
               'poids', 'taille', 'imc', 'production_lait', 'conso_aliment', 'gmq', 
               'pathologies', 'derniere_reproduction', 'date_enregistrement']
    writer.writerow(headers)
    
    for animal in animaux:
        row = [animal.get(h, '') for h in headers]
        writer.writerow(row)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'export_animaux_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification santé"""
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()})

# ================================================
# LANCEMENT
# ================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🐄 AnimTrack - Backend démarré")
    print("=" * 60)
    print(f"🌐 Serveur: http://localhost:5000")
    print(f"📁 Données: {os.path.abspath(DATA_FILE)}")
    print("=" * 60)
    print("\n📌 Identifiants générés automatiquement:")
    print("   Bovins  → B001, B002...")
    print("   Ovins   → O001, O002...")
    print("   Caprins → C001, C002...")
    print("   Porcins → P001, P002...")
    print("   Volaille→ V001, V002...")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
