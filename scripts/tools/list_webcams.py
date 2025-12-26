#!/usr/bin/env python3
"""
Listar todas las webcams disponibles
"""
import cv2

print("🔍 Buscando webcams disponibles...\n")

found = False
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ Webcam {i} DISPONIBLE")

        # Intentar leer un frame para confirmar
        ret, frame = cap.read()
        if ret:
            height, width = frame.shape[:2]
            print(f"   Resolución: {width}x{height}")

        cap.release()
        found = True
    else:
        print(f"❌ Webcam {i} no disponible")

if not found:
    print("\n⚠️  No se encontraron webcams")
else:
    print("\n✅ Usa el índice de la webcam que quieres en settings.yaml")
