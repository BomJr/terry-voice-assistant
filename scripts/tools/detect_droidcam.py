#!/usr/bin/env python3
"""
Detecta el índice de DroidCam como webcam
"""

import cv2
import sys

def test_camera(index):
    """Prueba si una cámara existe y funciona"""
    cap = cv2.VideoCapture(index)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        return ret and frame is not None
    return False

def main():
    print("🔍 Buscando DroidCam...\n")

    found = []
    for i in range(10):
        print(f"Probando índice {i}...", end=" ")
        if test_camera(i):
            print("✅ ENCONTRADA")
            found.append(i)
        else:
            print("❌")

    print("\n" + "="*50)
    if found:
        print(f"✅ Cámaras detectadas en índices: {found}")
        print(f"\n💡 Usa el índice {found[0]} para DroidCam")
        print(f"\nPara configurar Terry:")
        print(f"  webcam_index: {found[0]}")
    else:
        print("❌ No se detectó ninguna cámara")
        print("\nVerifica que:")
        print("  1. DroidCam esté conectado por USB")
        print("  2. En DroidCam Client hayas presionado 'Start'")
        print("  3. Terminal tenga permisos de cámara:")
        print("     Sistema > Privacidad > Cámara > Terminal")
    print("="*50)

if __name__ == "__main__":
    main()
