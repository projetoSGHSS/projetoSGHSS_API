import sqlite3

def conectar():
    return sqlite3.connect("projetoSGHSS.db")  # banco no mesmo diretório