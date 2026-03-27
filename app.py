import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CVA Generator 2026", page_icon="⚡", layout="wide")

# КОМАНДА

TEAM_NAME = "SINGULARITY"
TEAM_LOGO = "🚀"
CURRENT_YEAR = "2026"


# ДАННЫЕ ИНГИБИТОРОВ
INHIBITORS = {
    "inh_1 (2-Mercaptobenzothiazole)": {
        "id": 0,
        "base_efficiency": 92,
        "optimal_conc": [50, 200],
        "description": "Тиазольное соединение, эффективный ингибитор коррозии меди",
        "color": "#ff6b6b"
    },
    "inh_2 (4-benzylpiperazine)": {
        "id": 1,
        "base_efficiency": 85,
        "optimal_conc": [100, 300],
        "description": "Пиперазиновое производное, ингибитор для сталей",
        "color": "#4dabf7"
    },
    "inh_3 (benzothiazole)": {
        "id": 2,
        "base_efficiency": 78,
        "optimal_conc": [150, 400],
        "description": "Бензотиазол, классический ингибитор коррозии",
        "color": "#51cf66"
    },
    "inh_4 (Tolyltriazole)": {
        "id": 3,
        "base_efficiency": 95,
        "optimal_conc": [20, 100],
        "description": "Триазольное производное, эффективно для меди и алюминия",
        "color": "#be4bdb"
    }
}

# CSS ДЛЯ ТЕМНОГО ФОНА

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
    }
    .stMarkdown, .stText, .stTitle, .stHeader, .stCaption, label, p, div {
        color: #ffffff !important;
    }
    .css-1d391kg {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3a 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(77,171,247,0.5);
    }
    .info-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3a 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .success-card {
        background: linear-gradient(135deg, #1a2a1a 0%, #1e3a1e 100%);
        border-left: 4px solid #51cf66;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #2a2a1a 0%, #3a3a1e 100%);
        border-left: 4px solid #ffa94d;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .critical-card {
        background: linear-gradient(135deg, #2a1a1a 0%, #3a1e1e 100%);
        border-left: 4px solid #ff6b6b;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .stButton button {
        background: linear-gradient(135deg, #4dabf7 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(77,171,247,0.4);
    }
</style>
""", unsafe_allow_html=True)


# ФУНКЦИИ

def generate_curve(inhibitor_id, concentration):
    voltage = np.linspace(-1.2, 1.2, 1000)
    conc_factor = np.exp(-concentration / 500)
    inh_factor = 0.5 + inhibitor_id * 0.1
    amplitude = 0.8 * conc_factor * (1 - inhibitor_id * 0.05)
    
    peak_pos = 0.4 + inhibitor_id * 0.1
    peak_neg = -0.35 - inhibitor_id * 0.1
    
    current = amplitude * np.exp(-((voltage - peak_pos)**2)/0.1) - amplitude * 0.8 * np.exp(-((voltage - peak_neg)**2)/0.1)
    current += np.random.normal(0, 0.02, len(current))
    
    return voltage, current

def calculate_protection_efficiency(inhibitor_id, concentration, current_ratio, delta_e):
    inh_data = INHIBITORS[list(INHIBITORS.keys())[inhibitor_id]]
    base_eff = inh_data["base_efficiency"] / 100
    opt_low, opt_high = inh_data["optimal_conc"]
    
    if concentration < opt_low:
        conc_factor = concentration / opt_low
    elif concentration > opt_high:
        conc_factor = max(0, 1 - (concentration - opt_high) / opt_high)
    else:
        conc_factor = 1.0
    
    if current_ratio < 1.2 and delta_e < 0.1:
        electro_factor = 1.0
    elif current_ratio < 1.5 and delta_e < 0.2:
        electro_factor = 0.85
    elif current_ratio < 2.0:
        electro_factor = 0.7
    else:
        electro_factor = 0.5
    
    efficiency = base_eff * conc_factor * electro_factor * 100
    efficiency = min(98, max(5, efficiency))
    
    if efficiency >= 85:
        level = "Отличная защита"
        color = "#51cf66"
        icon = "✅"
    elif efficiency >= 70:
        level = "Хорошая защита"
        color = "#4dabf7"
        icon = "👍"
    elif efficiency >= 50:
        level = "Средняя защита"
        color = "#ffa94d"
        icon = "⚠️"
    elif efficiency >= 30:
        level = "Слабая защита"
        color = "#ffa94d"
        icon = "⚠️"
    else:
        level = "Плохая защита"
        color = "#ff6b6b"
        icon = "❌"
    
    return efficiency, level, color, icon

def create_plot(voltage, current, anode_idx, cathode_idx, title):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=voltage, y=current,
        mode='lines',
        name='CVA кривая',
        line=dict(color='#4dabf7', width=2.5),
        hovertemplate='<b>Потенциал</b>: %{x:.3f} В<br><b>Ток</b>: %{y:.3f} мА/см²<br><extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=[voltage[anode_idx]], y=[current[anode_idx]],
        mode='markers+text',
        name='Анодный пик',
        marker=dict(color='#ff6b6b', size=12, symbol='circle', line=dict(color='white', width=2)),
        text=[f"{current[anode_idx]:.3f}"],
        textposition='top center',
        textfont=dict(color='white', size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=[voltage[cathode_idx]], y=[current[cathode_idx]],
        mode='markers+text',
        name='Катодный пик',
        marker=dict(color='#51cf66', size=12, symbol='triangle-down', line=dict(color='white', width=2)),
        text=[f"{abs(current[cathode_idx]):.3f}"],
        textposition='bottom center',
        textfont=dict(color='white', size=10)
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=18, color='white')),
        xaxis_title="Потенциал, В (vs Ag/AgCl)",
        yaxis_title="Плотность тока, мА/см²",
        height=500,
        hovermode='closest',
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#0a0a0a',
        font=dict(color='white'),
        legend=dict(bgcolor='rgba(0,0,0,0.5)', font=dict(color='white')),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#2a2a3a', color='white'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#2a2a3a', color='white')
    )
    
    return fig

def create_pie_chart(efficiency, protection_level):
    remaining = 100 - efficiency
    
    labels = [f'Эффективность защиты\n{efficiency:.0f}%', f'Потери\n{remaining:.0f}%']
    values = [efficiency, remaining]
    colors = ['#51cf66', '#ff6b6b'] if efficiency > 50 else ['#ffa94d', '#ff6b6b']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hoverinfo='label+percent+value'
    )])
    
    fig.update_layout(
        title=dict(text="🛡️ Эффективность ингибирования", x=0.5, font=dict(size=16, color='white')),
        height=400,
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#0a0a0a',
        font=dict(color='white'),
        annotations=[
            dict(
                text=f"{efficiency:.0f}%",
                x=0.5, y=0.5,
                font_size=28,
                font_color='white',
                showarrow=False
            )
        ]
    )
    
    return fig

def create_charge_pie_chart(anodic_charge, cathodic_charge):
    total = anodic_charge + cathodic_charge
    if total == 0:
        total = 1
    
    anodic_percent = (anodic_charge / total) * 100
    cathodic_percent = (cathodic_charge / total) * 100
    
    labels = [f'Анодный заряд\n{anodic_percent:.1f}%', f'Катодный заряд\n{cathodic_percent:.1f}%']
    values = [anodic_charge, cathodic_charge]
    colors = ['#ff6b6b', '#51cf66']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textfont=dict(size=14, color='white'),
        hoverinfo='label+percent+value'
    )])
    
    fig.update_layout(
        title=dict(text="⚡ Распределение заряда", x=0.5, font=dict(size=16, color='white')),
        height=400,
        plot_bgcolor='#0a0a0a',
        paper_bgcolor='#0a0a0a',
        font=dict(color='white')
    )
    
    return fig


# ОСНОВНОЙ ИНТЕРФЕЙС

def main():
    # Заголовок
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 30px;">
        <h1 style="color: white; font-size: 3em;">{TEAM_LOGO} Генератор CVA-кривых {CURRENT_YEAR}</h1>
        <p style="color: white; font-size: 1.2em;">Разработано командой <strong style="font-size: 1.3em;">{TEAM_NAME}</strong></p>
        <p style="color: rgba(255,255,255,0.9);">Профессиональный инструмент для электрохимического анализа | Автоматическая генерация</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Боковая панель
    with st.sidebar:
        st.markdown("### 🎛️ Параметры эксперимента")
        
        inhibitor_name = st.selectbox("🧪 Выберите ингибитор", list(INHIBITORS.keys()))
        inh_data = INHIBITORS[inhibitor_name]
        
        st.markdown(f"""
        <div class="info-card">
            <p><strong>📊 Базовая эффективность:</strong> <span style="color: #51cf66;">{inh_data['base_efficiency']}%</span></p>
            <p><strong>🎯 Оптимальная концентрация:</strong> {inh_data['optimal_conc'][0]}-{inh_data['optimal_conc'][1]} ppm</p>
            <p><strong>📝 Описание:</strong> {inh_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        concentration = st.slider("📈 Концентрация (ppm)", 0, 1000, 100, 10)
        
        st.markdown("---")
        st.markdown(f"### 👥 Команда разработки")
        st.markdown(f"**{TEAM_NAME}**")
        st.markdown("Состав:")
        st.markdown("- Программист ML")
        st.markdown("- Программист-математик")
        st.markdown("- Химик-аналитик")
        
        st.markdown("---")
        st.markdown(f"### 📅 {CURRENT_YEAR}")
        st.markdown("Автоматическая генерация в реальном времени")
    
    # Автоматическая генерация
    inh_id = inh_data["id"]
    voltage, current = generate_curve(inh_id, concentration)
    
    # Поиск пиков
    anode_idx = np.argmax(current)
    cathode_idx = np.argmin(current)
    
    # Параметры
    anodic_current = current[anode_idx]
    cathodic_current = abs(current[cathode_idx])
    anodic_potential = voltage[anode_idx]
    cathodic_potential = voltage[cathode_idx]
    current_ratio = abs(anodic_current / cathodic_current) if cathodic_current != 0 else 0
    delta_e = abs(anodic_potential - cathodic_potential)
    
    # Расчет зарядов
    anodic_charge = np.trapz(np.maximum(current, 0), voltage)
    cathodic_charge = np.trapz(np.maximum(-current, 0), voltage)
    
    # Эффективность защиты
    efficiency, protection_level, protection_color, protection_icon = calculate_protection_efficiency(
        inh_id, concentration, current_ratio, delta_e
    )
    
    optimal_conc = inh_data["optimal_conc"]
    
    # Рекомендация
    if protection_level == "Отличная защита":
        recommendation = "✅ Идеальный режим защиты. Рекомендуется поддерживать текущие параметры."
    elif protection_level == "Хорошая защита":
        if concentration < optimal_conc[0]:
            recommendation = f"📈 Хорошая защита. Для повышения эффективности увеличьте концентрацию до {optimal_conc[0]} ppm."
        elif concentration > optimal_conc[1]:
            recommendation = f"💡 Хорошая защита. Для оптимизации расхода снизьте концентрацию до {optimal_conc[1]} ppm."
        else:
            recommendation = f"👍 Хорошая защита. Оптимальный диапазон концентрации: {optimal_conc[0]}-{optimal_conc[1]} ppm."
    elif protection_level == "Средняя защита":
        if current_ratio > 1.5:
            recommendation = f"⚠️ Средняя защита из-за асимметрии токов. Рекомендуется увеличить концентрацию до {optimal_conc[0] + 50} ppm."
        else:
            recommendation = f"⚠️ Средняя защита. Рекомендуется увеличить концентрацию до {optimal_conc[1]} ppm."
    elif protection_level == "Слабая защита":
        recommendation = f"⚠️ Слабая защита. Требуется значительное увеличение концентрации до {optimal_conc[1]} ppm или смена ингибитора."
    else:
        recommendation = "❌ Недостаточная защита. Рекомендуется сменить ингибитор на более эффективный."
    
    # Метрики
    st.markdown("### 📊 Ключевые параметры")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #ff6b6b;">Потенциал коррозии</h4>
            <h2 style="color: #ff6b6b;">{(anodic_potential + cathodic_potential)/2:.3f}</h2>
            <p style="color: #aaa;">E_corr, В</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #51cf66;">Ток коррозии</h4>
            <h2 style="color: #51cf66;">{(anodic_current + cathodic_current)/2:.3f}</h2>
            <p style="color: #aaa;">I_corr, мА/см²</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #4dabf7;">Поляризуемость</h4>
            <h2 style="color: #4dabf7;">{abs(anodic_potential - cathodic_potential):.3f}</h2>
            <p style="color: #aaa;">ΔE, В</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #be4bdb;">Скорость коррозии</h4>
            <h2 style="color: #be4bdb;">{(anodic_current + cathodic_current)/2 * 0.013:.3f}</h2>
            <p style="color: #aaa;">мм/год</p>
        </div>
        """, unsafe_allow_html=True)
    
    # График
    st.markdown("### 📈 CVA-кривая")
    title = f"{inhibitor_name} | {concentration} ppm"
    fig = create_plot(voltage, current, anode_idx, cathode_idx, title)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Круговые диаграммы
    st.markdown("### 📊 Визуализация эффективности")
    
    col_pie1, col_pie2 = st.columns(2)
    
    with col_pie1:
        fig_pie_efficiency = create_pie_chart(efficiency, protection_level)
        st.plotly_chart(fig_pie_efficiency, use_container_width=True, config={'displayModeBar': False})
    
    with col_pie2:
        fig_pie_charge = create_charge_pie_chart(anodic_charge, cathodic_charge)
        st.plotly_chart(fig_pie_charge, use_container_width=True, config={'displayModeBar': False})
    
    # Защита от коррозии
    st.markdown("### 🛡️ Оценка защиты от коррозии")
    
    col_prot1, col_prot2 = st.columns([1, 2])
    
    with col_prot1:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: {protection_color}20; border-radius: 15px; border: 2px solid {protection_color};">
            <h2 style="color: {protection_color}; font-size: 2.5em;">{protection_icon} {efficiency:.0f}%</h2>
            <h3 style="color: {protection_color};">{protection_level}</h3>
            <p style="color: {protection_color};">Эффективность ингибирования</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_prot2:
        st.markdown(f"""
        <div class="info-card">
            <h4>📋 Анализ защиты:</h4>
            <p>• <strong>Ингибитор:</strong> {inhibitor_name}</p>
            <p>• <strong>Концентрация:</strong> {concentration} ppm</p>
            <p>• <strong>Базовая эффективность:</strong> {inh_data['base_efficiency']}%</p>
            <p>• <strong>Потенциал коррозии:</strong> {(anodic_potential + cathodic_potential)/2:.3f} В</p>
            <p>• <strong>Ток коррозии:</strong> {(anodic_current + cathodic_current)/2:.3f} мА/см²</p>
            <p>• <strong>Скорость коррозии:</strong> {(anodic_current + cathodic_current)/2 * 0.013:.3f} мм/год</p>
            <p>• <strong>Оптимальная концентрация:</strong> {optimal_conc[0]}-{optimal_conc[1]} ppm</p>
            <p>• <strong>Рекомендация:</strong> {recommendation}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Дополнительные графики
    st.markdown("### 📊 Анализ распределения")
    
    col_hist, col_bar = st.columns(2)
    
    with col_hist:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(x=current, nbinsx=50, marker_color='#4dabf7', opacity=0.7))
        fig_hist.update_layout(
            title="Распределение плотности тока",
            xaxis_title="Ток, мА/см²",
            yaxis_title="Частота",
            height=400,
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='white'),
            xaxis=dict(color='white', gridcolor='#2a2a3a'),
            yaxis=dict(color='white', gridcolor='#2a2a3a')
        )
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})
    
    with col_bar:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=['Анодный', 'Катодный'],
            y=[anodic_current, cathodic_current],
            marker_color=['#ff6b6b', '#51cf66'],
            text=[f"{anodic_current:.3f}", f"{cathodic_current:.3f}"],
            textposition='outside',
            textfont=dict(color='white')
        ))
        fig_bar.update_layout(
            title="Сравнение анодного и катодного токов",
            yaxis_title="Ток, мА/см²",
            height=400,
            plot_bgcolor='#0a0a0a',
            paper_bgcolor='#0a0a0a',
            font=dict(color='white'),
            xaxis=dict(color='white'),
            yaxis=dict(color='white', gridcolor='#2a2a3a')
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
    
    # Экспорт данных
    st.markdown("### 💾 Экспорт данных")
    
    df = pd.DataFrame({
        "Потенциал_В": voltage,
        "Ток_мА_см2": current
    })
    
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            "📥 Скачать CSV",
            df.to_csv(index=False),
            f"cva_{inh_data['id']}_{concentration}ppm.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col_exp2:
        params_df = pd.DataFrame([
            {"Параметр": "Потенциал коррозии", "Значение": f"{(anodic_potential + cathodic_potential)/2:.3f} В"},
            {"Параметр": "Ток коррозии", "Значение": f"{(anodic_current + cathodic_current)/2:.3f} мА/см²"},
            {"Параметр": "Поляризуемость ΔE", "Значение": f"{delta_e:.3f} В"},
            {"Параметр": "Скорость коррозии", "Значение": f"{(anodic_current + cathodic_current)/2 * 0.013:.3f} мм/год"},
            {"Параметр": "Анодный заряд", "Значение": f"{anodic_charge:.3f} мКл/см²"},
            {"Параметр": "Катодный заряд", "Значение": f"{cathodic_charge:.3f} мКл/см²"},
            {"Параметр": "Эффективность защиты", "Значение": f"{efficiency:.0f}% ({protection_level})"}
        ])
        st.download_button(
            "📊 Скачать параметры",
            params_df.to_csv(index=False),
            f"params_{inh_data['id']}_{concentration}ppm.csv",
            "text/csv",
            use_container_width=True
        )
    
    # Футер
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 20px; color: #666;">
        <p>© {CURRENT_YEAR} Команда {TEAM_NAME} | Инструмент для генерации синтетических CVA-кривых</p>
        <p style="font-size: 0.8em;">Автоматическая генерация в реальном времени</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
