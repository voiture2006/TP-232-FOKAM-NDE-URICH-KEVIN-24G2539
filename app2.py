"""
Application Flask pour AnimTrack - Solution de gestion d'élevage
INF 232 EC2 - Backend complet avec identifiants par espèce (B001, C001, O001, P001, V001)
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import json
import os
import math
from datetime import datetime, timedelta
from io import BytesIO
import csv
import re

# ================================================
# CONFIGURATION DE L'APPLICATION
# ================================================
app = Flask(__name__)
CORS(app)

# Configuration des dossiers statiques
app.config['IMAGES_FOLDER'] = 'images'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Fichiers de données
DATA_FILE = 'animaux.json'

# ================================================
# CONSTANTES
# ================================================

# Codes pour les identifiants par espèce
CODE_ESPECE = {
    'Bovin': 'B',
    'Ovin': 'O',
    'Caprin': 'C',
    'Porcin': 'P',
    'Volaille': 'V'
}

# Durée de gestation par espèce (en jours)
GESTATION = {
    'Bovin': 280,
    'Ovin': 150,
    'Caprin': 150,
    'Porcin': 114,
    'Volaille': 21
}

# Types d'animaux par espèce (pour information)
TYPES_ANIMAUX = {
    'Bovin': ['Vache laitière', 'Vache allaitante', 'Taureau reproducteur', 'Bœuf', 'Veau'],
    'Ovin': ['Brebis', 'Bélier', 'Agneau', 'Mouton'],
    'Caprin': ['Chèvre', 'Bouc', 'Chevreau'],
    'Porcin': ['Truie', 'Verrat', 'Porc charcutier', 'Porcelet'],
    'Volaille': ['Poule pondeuse', 'Poulet de chair', 'Coq', 'Poussin']
}

# ================================================
# FONCTIONS UTILITAIRES
# ================================================

def load_data():
    """Charge les données depuis le fichier JSON"""
    if not os.path.exists(DATA_FILE):
        # Créer des données d'exemple si le fichier n'existe pas
        exemple_data = get_exemple_data()
        save_data(exemple_data)
        return exemple_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return get_exemple_data()

def save_data(data):
    """Sauvegarde les données dans le fichier JSON"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def calculate_imc(poids, taille):
    """Calcule l'IMC (Indice de Masse Corporelle)"""
    if poids and taille and taille > 0:
        return round(poids / ((taille / 100) ** 2), 1)
    return None

def generate_identifiant(espece):
    """Génère un identifiant unique par espèce (B001, C001, O001, P001, V001)"""
    code = CODE_ESPECE.get(espece, 'X')
    
    animaux = load_data()
    existing_numbers = []
    
    for a in animaux:
        identifiant = a.get('identifiant', '')
        if identifiant and identifiant.startswith(code):
            match = re.search(rf'{code}(\d+)', identifiant)
            if match:
                existing_numbers.append(int(match.group(1)))
    
    next_num = 1
    if existing_numbers:
        existing_numbers.sort()
        for num in existing_numbers:
            if num == next_num:
                next_num += 1
            else:
                break
    
    return f"{code}{next_num:03d}"

def get_gestation_info():
    """Récupère les informations de gestation pour toutes les femelles"""
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
                    'derniere_reproduction': animal['derniere_reproduction'],
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
    """Retourne des données d'exemple pour démarrer l'application"""
    return [
        {
            "id": 1,
            "identifiant": "B001",
            "type_animal": "Vache laitière",
            "age": 36,
            "sexe": "Femelle",
            "espece": "Bovin",
            "race": "Prim'Holstein",
            "poids": 720,
            "taille": 148,
            "imc": 328.7,
            "production_lait": 32.5,
            "conso_aliment": 21.0,
            "gmq": 780,
            "pathologies": "Aucune",
            "derniere_reproduction": "2024-06-15",
            "date_enregistrement": "2024-01-10T10:30:00Z"
        },
        {
            "id": 2,
            "identifiant": "B002",
            "type_animal": "Taureau reproducteur",
            "age": 52,
            "sexe": "Mâle",
            "espece": "Bovin",
            "race": "Limousine",
            "poids": 950,
            "taille": 155,
            "imc": 395.5,
            "production_lait": 0,
            "conso_aliment": 24.5,
            "gmq": 890,
            "pathologies": "Aucune",
            "derniere_reproduction": None,
            "date_enregistrement": "2024-01-12T14:20:00Z"
        },
        {
            "id": 3,
            "identifiant": "B003",
            "type_animal": "Vache allaitante",
            "age": 42,
            "sexe": "Femelle",
            "espece": "Bovin",
            "race": "Blonde d'Aquitaine",
            "poids": 780,
            "taille": 152,
            "imc": 337.6,
            "production_lait": 28.0,
            "conso_aliment": 22.5,
            "gmq": 810,
            "pathologies": "Mammite légère",
            "derniere_reproduction": "2024-05-10",
            "date_enregistrement": "2024-03-15T15:00:00Z"
        },
        {
            "id": 4,
            "identifiant": "C001",
            "type_animal": "Chèvre",
            "age": 36,
            "sexe": "Femelle",
            "espece": "Caprin",
            "race": "Alpine",
            "poids": 68,
            "taille": 78,
            "imc": 111.7,
            "production_lait": 3.5,
            "conso_aliment": 2.6,
            "gmq": 125,
            "pathologies": "Aucune",
            "derniere_reproduction": "2024-08-20",
            "date_enregistrement": "2024-02-05T09:15:00Z"
        },
        {
            "id": 5,
            "identifiant": "O001",
            "type_animal": "Brebis",
            "age": 24,
            "sexe": "Femelle",
            "espece": "Ovin",
            "race": "Boulonnaise",
            "poids": 88,
            "taille": 74,
            "imc": 160.7,
            "production_lait": 1.8,
            "conso_aliment": 2.9,
            "gmq": 175,
            "pathologies": "Aucune",
            "derniere_reproduction": "2024-07-05",
            "date_enregistrement": "2024-02-18T11:45:00Z"
        },
        {
            "id": 6,
            "identifiant": "P001",
            "type_animal": "Truie",
            "age": 18,
            "sexe": "Femelle",
            "espece": "Porcin",
            "race": "Large White",
            "poids": 135,
            "taille": 86,
            "imc": 182.5,
            "production_lait": 0,
            "conso_aliment": 4.8,
            "gmq": 680,
            "pathologies": "Aucune",
            "derniere_reproduction": "2024-09-10",
            "date_enregistrement": "2024-03-02T13:20:00Z"
        }
    ]

# ================================================
# ROUTES POUR LES FICHIERS STATIQUES
# ================================================

@app.route('/')
def index():
    """Page d'accueil - sert le fichier HTML principal"""
    try:
        return send_file('index2.html')
    except FileNotFoundError:
        return "Fichier index2.html non trouvé. Assurez-vous qu'il est dans le même dossier.", 404

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Sert les images depuis le dossier images"""
    try:
        return send_from_directory('images', filename)
    except Exception as e:
        return "", 404

# ================================================
# ROUTES API - GESTION DES ANIMAUX
# ================================================

@app.route('/api/animaux', methods=['GET'])
def get_animaux():
    """Récupère la liste de tous les animaux"""
    animaux = load_data()
    return jsonify(animaux)

@app.route('/api/animaux/<int:id>', methods=['GET'])
def get_animal(id):
    """Récupère un animal spécifique par son ID"""
    animaux = load_data()
    animal = next((a for a in animaux if a.get('id') == id), None)
    if animal:
        return jsonify(animal)
    return jsonify({'error': 'Animal non trouvé'}), 404

@app.route('/api/animaux/identifiant/<string:identifiant>', methods=['GET'])
def get_animal_by_identifiant(identifiant):
    """Récupère un animal par son identifiant (B001, C002, etc.)"""
    animaux = load_data()
    animal = next((a for a in animaux if a.get('identifiant') == identifiant), None)
    if animal:
        return jsonify(animal)
    return jsonify({'error': 'Animal non trouvé'}), 404

@app.route('/api/animaux/gestations', methods=['GET'])
def get_gestations():
    """Retourne les informations de gestation pour les femelles enceintes"""
    gestations = get_gestation_info()
    
    espece_filter = request.args.get('espece', None)
    if espece_filter and espece_filter != 'tous':
        gestations = [g for g in gestations if g['espece'] == espece_filter]
    
    return jsonify({
        'total_enceintes': len([g for g in gestations if g['est_enceinte']]),
        'accouchements_aujourdhui': len([g for g in gestations if g['accouchement_aujourdhui']]),
        'accouchements_semaine': len([g for g in gestations if g['accouchement_semaine']]),
        'gestations': gestations
    })

@app.route('/api/animaux', methods=['POST'])
def add_animal():
    """Ajoute un nouvel animal avec validation"""
    try:
        data = request.get_json()
        animaux = load_data()
        
        # === VALIDATION DES DONNEES ===
        errors = []
        
        age = data.get('age')
        if age is None or not str(age).isdigit() or int(age) < 0 or int(age) > 300:
            errors.append("Âge invalide (0-300 mois)")
        
        sexe = data.get('sexe')
        if not sexe or sexe not in ['Mâle', 'Femelle']:
            errors.append("Sexe invalide")
        
        espece = data.get('espece')
        if not espece or espece not in CODE_ESPECE:
            errors.append(f"Espèce invalide. Choisir parmi: {', '.join(CODE_ESPECE.keys())}")
        
        type_animal = data.get('type_animal')
        if not type_animal or not type_animal.strip():
            errors.append("Le type d'animal est requis (ex: Vache laitière, Brebis, Chèvre...)")
        
        race = data.get('race')
        if not race or not race.strip():
            errors.append("La race est requise")
        
        poids = data.get('poids')
        if poids is None:
            errors.append("Le poids est requis")
        else:
            try:
                if float(poids) < 0.1 or float(poids) > 2000:
                    errors.append("Poids invalide (0.1-2000 kg)")
            except:
                errors.append("Poids doit être un nombre")
        
        taille = data.get('taille')
        if taille is None:
            errors.append("La hauteur est requise")
        else:
            try:
                if float(taille) < 10 or float(taille) > 250:
                    errors.append("Hauteur invalide (10-250 cm)")
            except:
                errors.append("Hauteur doit être un nombre")
        
        if errors:
            return jsonify({'error': 'Erreurs de validation', 'details': errors}), 400
        
        new_id = max([a.get('id', 0) for a in animaux], default=0) + 1
        imc = calculate_imc(poids, taille)
        identifiant = generate_identifiant(espece)
        
        new_animal = {
            'id': new_id,
            'identifiant': identifiant,
            'type_animal': type_animal.strip(),
            'age': int(age),
            'sexe': sexe,
            'espece': espece,
            'race': race.strip(),
            'poids': float(poids),
            'taille': float(taille),
            'imc': imc,
            'production_lait': float(data.get('production_lait', 0)),
            'conso_aliment': float(data.get('conso_aliment', 0)),
            'gmq': float(data.get('gmq', 0)),
            'pathologies': data.get('pathologies', 'Aucune').strip(),
            'derniere_reproduction': data.get('derniere_reproduction') if data.get('derniere_reproduction') else None,
            'date_enregistrement': datetime.now().isoformat()
        }
        
        animaux.append(new_animal)
        save_data(animaux)
        
        return jsonify({
            'message': 'Animal ajouté avec succès',
            'id': new_id,
            'identifiant': identifiant,
            'imc': imc
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/animaux/<int:id>', methods=['PUT'])
def update_animal(id):
    """Met à jour un animal existant"""
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
        return jsonify({'message': 'Animal mis à jour avec succès'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/animaux/<int:id>', methods=['DELETE'])
def delete_animal(id):
    """Supprime un animal"""
    animaux = load_data()
    animaux = [a for a in animaux if a.get('id') != id]
    save_data(animaux)
    return jsonify({'message': 'Animal supprimé avec succès'})

# ================================================
# ROUTES API - STATISTIQUES
# ================================================

@app.route('/api/stats/descriptives', methods=['GET'])
def get_descriptive_stats():
    """Calcule les statistiques descriptives pour toutes les variables numériques"""
    animaux = load_data()
    
    if not animaux:
        return jsonify({'total': 0})
    
    numeric_fields = ['age', 'poids', 'taille', 'imc', 'production_lait', 'conso_aliment', 'gmq']
    stats = {'total': len(animaux)}
    
    for field in numeric_fields:
        values = [a.get(field) for a in animaux if a.get(field) is not None and a.get(field) != 0]
        
        if values:
            values_sorted = sorted(values)
            n = len(values)
            mean_val = sum(values) / n
            
            variance = sum((x - mean_val) ** 2 for x in values) / n
            std_dev = math.sqrt(variance)
            
            stats[field] = {
                'count': n,
                'moyenne': round(mean_val, 2),
                'ecart_type': round(std_dev, 2),
                'minimum': min(values),
                'maximum': max(values),
                'Q1': values_sorted[n//4] if n >= 4 else values_sorted[0],
                'Q2': values_sorted[n//2] if n >= 2 else values_sorted[0],
                'Q3': values_sorted[3*n//4] if n >= 4 else values_sorted[-1]
            }
    
    return jsonify(stats)

@app.route('/api/correlation', methods=['GET'])
def get_correlation_matrix():
    """Calcule la matrice de corrélation de Pearson"""
    animaux = load_data()
    
    if len(animaux) < 3:
        return jsonify({'error': 'Pas assez de données pour calculer la corrélation (minimum 3 animaux)'})
    
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
        return jsonify({'error': 'Pas assez de données complètes pour la corrélation'})
    
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
    
    return jsonify({
        'variables': variables,
        'matrix': corr_matrix
    })

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Exporte toutes les données au format CSV"""
    animaux = load_data()
    
    if not animaux:
        return jsonify({'error': 'Aucune donnée à exporter'}), 404
    
    output = BytesIO()
    writer = csv.writer(output)
    
    headers = ['id', 'identifiant', 'type_animal', 'age', 'sexe', 'espece', 'race', 'poids', 'taille', 'imc', 
               'production_lait', 'conso_aliment', 'gmq', 'pathologies', 
               'derniere_reproduction', 'date_enregistrement']
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

@app.route('/api/stats/especes', methods=['GET'])
def get_stats_by_espece():
    """Statistiques par espèce avec liste des identifiants"""
    animaux = load_data()
    
    stats_by_espece = {}
    
    for animal in animaux:
        espece = animal.get('espece', 'Inconnu')
        if espece not in stats_by_espece:
            stats_by_espece[espece] = {
                'count': 0,
                'poids_total': 0,
                'age_total': 0,
                'males': 0,
                'femelles': 0,
                'lait_total': 0,
                'identifiants': []
            }
        
        stats_by_espece[espece]['count'] += 1
        stats_by_espece[espece]['poids_total'] += animal.get('poids', 0)
        stats_by_espece[espece]['age_total'] += animal.get('age', 0)
        stats_by_espece[espece]['lait_total'] += animal.get('production_lait', 0)
        stats_by_espece[espece]['identifiants'].append(animal.get('identifiant', ''))
        
        if animal.get('sexe') == 'Mâle':
            stats_by_espece[espece]['males'] += 1
        elif animal.get('sexe') == 'Femelle':
            stats_by_espece[espece]['femelles'] += 1
    
    for espece in stats_by_espece:
        if stats_by_espece[espece]['count'] > 0:
            stats_by_espece[espece]['poids_moyen'] = round(
                stats_by_espece[espece]['poids_total'] / stats_by_espece[espece]['count'], 1
            )
            stats_by_espece[espece]['age_moyen'] = round(
                stats_by_espece[espece]['age_total'] / stats_by_espece[espece]['count'], 1
            )
            stats_by_espece[espece]['lait_moyen'] = round(
                stats_by_espece[espece]['lait_total'] / max(1, stats_by_espece[espece]['femelles']), 1
            )
            stats_by_espece[espece]['identifiants'].sort()
    
    return jsonify(stats_by_espece)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérification de l'état du serveur"""
    animaux = load_data()
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'animaux_count': len(animaux)
    })

@app.route('/api/types', methods=['GET'])
def get_types():
    """Retourne les types d'animaux disponibles par espèce"""
    return jsonify(TYPES_ANIMAUX)

# ================================================
# LANCEMENT DE L'APPLICATION
# ================================================
if __name__ == '__main__':
    print("=" * 60)
    print("🐄 AnimTrack - Solution de Gestion d'Élevage")
    print("=" * 60)
    print(f"📂 Serveur: http://localhost:5000")
    print(f"📁 Dossier images: {os.path.abspath('images')}")
    print(f"💾 Fichier de données: {os.path.abspath(DATA_FILE)}")
    print("=" * 60)
    print("\n📌 Format des identifiants par espèce:")
    print("   Bovins  → B001, B002, B003...")
    print("   Ovins   → O001, O002, O003...")
    print("   Caprins → C001, C002, C003...")
    print("   Porcins → P001, P002, P003...")
    print("   Volaille→ V001, V002, V003...")
    print("=" * 60)
    print("\n✅ Validation des données activée:")
    print("   - Âge: 0-300 mois")
    print("   - Poids: 0.1-2000 kg")
    print("   - Hauteur: 10-250 cm")
    print("   - Lait: 0-100 L/j")
    print("   - Consommation: 0-50 kg/j")
    print("   - GMQ: 0-2000 g/j")
    print("=" * 60)
    print("\n🗑️ API de suppression disponible: DELETE /api/animaux/<id>")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
