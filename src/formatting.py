import streamlit as st
import pandas as pd
import locale
from streamlit import column_config

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def colorir_semestres(row: pd.Series):
    """Aplica uma cor de fundo diferente para linhas de semestres pares."""
    cor = "#2e2f31"
    if row['Semestre'] % 2 == 0:
        return [f'background-color: {cor}'] * len(row)
    return [''] * len(row)

def formatador_k(valor, pos):
    """
    Recebe um valor e o formata para o padrão 'R$ Xk'.
    Ex: 10000 -> R$ 10k
    """
    return f'R$ {int(valor / 1000)}k'

def format_currency(value):
    return locale.currency(value, grouping=True, symbol=True)

def formatar_valor_brl(valor):
    """Formata um número como moeda brasileira (R$ 1.234,56)."""
    if isinstance(valor, (int, float)):
        return f'R$ {valor:_.2f}'.replace('.', ',').replace('_', '.')
    return valor