import json

def conjugate_imperfect(infinitive, persona_base):
    # 1. Manejo de los ÚNICOS tres verbos irregulares en imperfecto
    irregulars = {
        "ser": {
            "yo": "era", "tú": "eras", "él/ella/usted": "era", 
            "nosotros": "éramos", "vosotros": "erais", "ellos/ellas/ustedes": "eran"
        },
        "ir": {
            "yo": "iba", "tú": "ibas", "él/ella/usted": "iba", 
            "nosotros": "íbamos", "vosotros": "ibais", "ellos/ellas/ustedes": "iban"
        },
        "ver": {
            "yo": "veía", "tú": "veías", "él/ella/usted": "veía", 
            "nosotros": "veíamos", "vosotros": "veíais", "ellos/ellas/ustedes": "veían"
        }
    }

    if infinitive in irregulars:
        return irregulars[infinitive].get(persona_base, "")

    # 2. Lógica para verbos regulares
    stem = infinitive[:-2] # Quita el 'ar', 'er', o 'ir'
    ending_type = infinitive[-2:] # Identifica si termina en 'ar', 'er', 'ir'

    if ending_type == "ar":
        endings = {
            "yo": "aba", "tú": "abas", "él/ella/usted": "aba", 
            "nosotros": "ábamos", "vosotros": "abais", "ellos/ellas/ustedes": "aban"
        }
    elif ending_type in ["er", "ir"]:
        endings = {
            "yo": "ía", "tú": "ías", "él/ella/usted": "ía", 
            "nosotros": "íamos", "vosotros": "íais", "ellos/ellas/ustedes": "ían"
        }
    else:
        return "" # Por si hay algún error tipográfico en el infinitivo

    return stem + endings.get(persona_base, "")

def convert_to_imperfect(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

        for entry in data:
            # Actualizamos el nombre del tiempo
            entry["tiempo"] = "imperfecto"
            
            infinitive = entry["infinitivo"]
            persona_base = entry["persona_base"]
            
            # Generamos la nueva conjugación en imperfecto
            new_forma = conjugate_imperfect(infinitive, persona_base)
            if new_forma:
                entry["forma"] = new_forma
                
            # Actualizamos la traducción de 'would' a 'used to'
            entry["traducción"] = entry["traducción"].replace("would", "used to")

            # Las etiquetas como "tipo_verbo" se mantienen intactas automáticamente

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"¡Éxito! Se han convertido {len(data)} entradas al Imperfecto en '{output_file}'")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Ejecutar la conversión
convert_to_imperfect('banco_condicional.json', 'banco_imperfecto.json')
