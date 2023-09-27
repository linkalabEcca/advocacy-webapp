import streamlit as st
import pandas as pd
import streamlit_scrollable_textbox as stx
import numpy as np
import base64
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb





df = pd.read_excel('data/dataset_app.xlsx').dropna()

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_excel('report_advocacy', engine='xlsxwriter',index=False)#.encode('utf-8')

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_bg(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = """
        <style>
        .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        }
        </style>
    """ % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def regolarize_scores(df,num_score_1,num_score_2,num_score_3):
    
    s_Sm = num_score_1[0]
    s_Sk = num_score_1[1]

    s_Sv1 = num_score_2[0]
    s_Sv2 = num_score_2[1]

    s_SM = num_score_3[0]
    s_SV = num_score_3[1]

    
    df['Complete_Score_manager'] = ((s_Sk * df['SimilarityScore_keywords_semantic'] + (s_Sm * df['Complete_Score_manager']))/2)
    df[['Complete_Score_manager']] = scaler.fit_transform(df[['Complete_Score_manager']])

    df['Virality_Score_Searchs'] = df['Virality_Score_2.wiki'] + df['Virality_Score_3.gtrends']
    df[['Virality_Score_Searchs']] = scaler.fit_transform(df[['Virality_Score_Searchs']])

    df['Virality_Score'] = ((s_Sv1 * df['Virality_Score_1.gnews'] + (s_Sv2 * df['Virality_Score_Searchs']))/2)
    df[['Virality_Score']] = scaler.fit_transform(df[['Virality_Score']])


    df['Final_Score'] = ((s_SV * df['Virality_Score'] + (s_SM * df['Complete_Score_manager']))/2)
    df[['Final_Score']] = scaler.fit_transform(df[['Final_Score']])
    
    df = df.sort_values('Final_Score',ascending = False)
    
    return df

def slider_scores(n_key,s1_name,s2_name,S1,S2, v1,v2,check):
    
    scores_Sm = st.select_slider(
    '',
    options=[f'{s1_name}', f'{S1} (0.1 - 0.9) {S2}', f'{S1} (0.2 - 0.8) {S2}', f'{S1} (0.3 - 0.7) {S2}', f'{S1} (0.4 - 0.6) {S2}', f'{S1} (0.5 - 0.5) {S2}',f'{S1} (0.6 - 0.4) {S2}',f'{S1} (0.7 - 0.3) {S2}',f'{S1} (0.8 - 0.2) {S2}',f'{S1} (0.9 - 0.1) {S2}', f'{s2_name}'],key = n_key,value=f'{S1} ({v1} - {v2}) {S2}', label_visibility="collapsed", disabled=check)




    
    if scores_Sm == f'{s1_name}':
        num = (0,1)
    if scores_Sm == scores_Sm ==  f'{S1} (0.1 - 0.9) {S2}':
        num = (0.1,0.9)
    if scores_Sm == f'{S1} (0.2 - 0.8) {S2}':
        num = (0.2,0.8)
    if scores_Sm == f'{S1} (0.3 - 0.7) {S2}':
        num = (0.3,0.7)
    if scores_Sm == f'{S1} (0.4 - 0.6) {S2}':
        num = (0.4,0.6)
    if scores_Sm == f'{S1} (0.5 - 0.5) {S2}':
        num = (0.5,0.5)
    if scores_Sm == f'{S1} (0.6 - 0.4) {S2}':
        num = (0.6,0.4)
    if scores_Sm == f'{S1} (0.7 - 0.3) {S2}':
        num = (0.7,0.3)
    if scores_Sm == f'{S1} (0.8 - 0.2) {S2}':
        num = (0.8,0.2)
    if scores_Sm == f'{S1} (0.9 - 0.1) {S2}':
        num = (0.9,0.1)
    if scores_Sm == f'{s2_name}':
        num = (1,0)
        
    #NB = num[0] * 100   
    NB=20
    ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
    background: rgb(1 1 1 / 0%);color: black /100%; } </style>''', unsafe_allow_html = True)


    Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
    background-color: black;color: black; box-shadow: rgb(14 38 74 / 60%) 0px 0px 0px 0.3rem;} </style>''', unsafe_allow_html = True)

    
    Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                { color: black; } </style>''', unsafe_allow_html = True)

    col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
        background: linear-gradient(to right, yellow 0%, 
                                    yellow {NB}%, 
                                        yellow {NB}%,                    
                                  red 100%);
                                  color: black; }} </style>'''
    
    ColorSlider_ = st.markdown(col, unsafe_allow_html = True) 

    return num

def dataframe_with_selections(df):
    df_with_selections = df#.copy()
    df_with_selections.insert(0, "Select", False)
    
    heading_properties = [('font-size', '16px'),('text-align', 'center'),
                      ('color', 'black'),  ('font-weight', 'bold'),
                      ('background', 'mediumturquoise'),('border', '1.2px solid')]
    
    dfstyle = [{"selector":"th", "props": heading_properties}]#,
              # {"selector": "td", "props": cell_properties}]
    
    edited_df = st.data_editor(
    df_with_selections[['Select','data','title','domain','Final_Score','Complete_Score_manager','Virality_Score', 'source','Permalink']].style.set_table_styles(dfstyle).set_properties(**{'background-color': 'azure'},subset=['Virality_Score']).set_properties(**{'background-color': 'rgb(50 205 50 / 10%)'},subset=['Final_Score']).set_properties(**{'background-color': 'rgb(255 215 0 / 10%)'},subset=['Complete_Score_manager', ]),#.highlight_max(axis=0,subset=['Final_Score', 'Virality_Score']),#style.set_properties(**{'background-color': 'red'}, subset=['title']),
        key="data_editor",
        hide_index=True,
       # disabled=("title"),
        column_config=column_configuration
        
    )

    selected_rows = edited_df[edited_df.Select]
    #st.write(selected_rows)
    
    return selected_rows.drop('Select', axis=1), selected_rows.index



def get_values_news(df,index):



    try:
        dominio = df.loc[index]['domain'].values[0]
        testo = df.loc[index]['message'].values[0]
        titolo = df.loc[index]['title'].values[0]
        summary = df.loc[index]['summary'].values[0]
        url = df.loc[index]['Permalink'].values[0]
        source = df.loc[index]['source'].values[0]

        Sm = round(df.loc[index]['Complete_Score_manager'].values[0],2)
        Sv = round(df.loc[index]['Virality_Score'].values[0],2)
        Sa = round(df.loc[index]['Final_Score'].values[0],2)
    except:
        dominio = df.loc[index]['domain']
        testo = df.loc[index]['message']
        titolo = df.loc[index]['title']
        summary = df.loc[index]['summary']
        url = df.loc[index]['Permalink']
       #try:
       #    url = df.loc[index]['Permalink']
       #except:
       #    url = 'None'
        source = df.loc[index]['source']


        Sm = round(df.loc[index]['Complete_Score_manager'],2)
        Sv = round(df.loc[index]['Virality_Score'],2)
        Sa = round(df.loc[index]['Final_Score'],2)

    return dominio,testo,titolo,summary,url,source,Sm,Sv,Sa

#################################################################################################################################
#################################################################################################################################


st.set_page_config(
    page_title="Advocacy - Web App",
    page_icon=":newspaper:",
    layout="wide"
)    


with st.sidebar:
    st.markdown(f"<h1 style='text-align: center;color:black '> ADVOCACY </h1>", unsafe_allow_html=True)
    st.image('data/logo/eni_22.jpg')

#st.markdown('Demo della futura dashboard per il progetto Advocacy :newspaper:')
st.markdown("""<hr style="height:2px;border:none;color:black;background-color:black;" /> """,
            unsafe_allow_html=True)
c0,c1, c2,  c4,c5 = st.columns((3,10.2,  1, 2,1))

with c1:
    st.markdown(f"<h1 style='text-align: center;color:black '> ADVOCACY - Web App </h1>", unsafe_allow_html=True)
    

with c4:
    #st.write('')
    st.image('data/logo/eni_22.jpg')
c0,c1, c2,  c4,c5 = st.columns((3,10.2,  1, 2,1))
with c1:
    with st.expander('📌 :grey[***Clicca per maggiori info sul progetto***] 📌', expanded=False):

            st.markdown(f"<h5 style='text-align: left;color:black '>👨‍💼 Contesto 👨‍💼 </h1>", unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>Il dipartimento DEN B al momento fornisce, tramite mail settimanale, una selezione manuale di articoli/argomenti (ci sono argomenti che sono di particolare interesse: es. digitalizzazione, coerenti con il piano editoriale) da suggerire a top manager. La selezione avviene attraverso la lettura e analisi di articoli pubblicati su testate giornalistiche “attenzionate”, ovvero appartenenti ad una lista. Nella mail settimanale gli articoli selezionati manualmente sono raggruppati per tema e sono utilizzati come spunto/suggerimento per redigere un testo (tweet o post) da pubblicare sui profili social dei top manager.", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: left;color:black '>🎯 Obiettivo 🎯</h1>", unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>Creare strumento per automatizzare la selezione dell’articolo/argomento che top manager + figure rilevanti sui social dovranno condividere sui loro profili social", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: left;color:black '>📊 Sviluppo 📊 </h1>", unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>Sviluppare un sistema di raccomandazione che analizzi il comportamento sui social (Twitter, Linkedin) dei top manager+figure rilevanti (=partecipanti progetto advocacy). A partire dalle pubblicazioni dell’ultimo anno, dedurne indicatori rilevanti (frequenza pubblicazione articoli, temi affrontati, viralità/n. condivisioni post) e associarli all’utente (dipartimento Eni di appartenenza, principali temi di interesse, etc.). La finalità è di personalizzare la selezione degli articoli in base a comportamento dell’utente analizzato. Sarebbe interessante definire anche un criterio di “affinità” di nuovi articol/temii sulla base del comportamento di un utente.", unsafe_allow_html=True)





#set_bg('data/sfondo.jpg')    

#df_2 = pd.read_excel('data/dataset_app.xlsx')
scaler = MinMaxScaler()

column_configuration = {
       "data": st.column_config.DatetimeColumn(
        "Data", help="The date of the article", format="D MMM YYYY", #format="D MMM YYYY, h:mm a",
           width=80,
    ),
        'title': st.column_config.TextColumn(
        'Title', help="The title of the article", max_chars=100,
             width=200,
    ),
    'domain': st.column_config.TextColumn(
        'Domain', help="The domain of the article", max_chars=100,
             #width=200,
    ),
    "Permalink": st.column_config.LinkColumn(
        "Url", help="Link article",
         validate="^https://[a-z]+\.streamlit\.app$",
            max_chars=100,
        width=200,
    ),
        'Complete_Score_manager': st.column_config.ProgressColumn(
            'Manager Score',
            help="Score calculated based on the manager's preferences",
            format="%.2f",
            width=100,
        
        ),
    'Virality_Score': st.column_config.ProgressColumn(
            'Virality Score ',
            help="score calculated based on the most viral searches and news of the week",
            format="%.2f",
            width=100,
 ),
    'Final_Score': st.column_config.ProgressColumn(
            'Advocacy Score',
            help="score calculated based on the most viral searches and news of the week",
            format="%.2f",
            width=100,
 ),
          'source': st.column_config.TextColumn(
        'Source', help="The source who forwarded the article", max_chars=100,
             width=57,
    ),
    "Select": st.column_config.CheckboxColumn('S',
            #default=1,required=False,disabled=False,
             width=30,)
    
}




#[data-testid="column"] {
#    box-shadow: rgb(0 0 0 / 20%) 0px 2px 1px -1px, rgb(0 0 0 / 14%) 0px 1px 1px 0px, rgb(0 0 0 / 12%) 0px 1px 3px 0px;
#    border-radius: 15px;
#    padding: 5% 5% 5% 10%;
#} ##DA AGGIUNGERE PER COLONNE

st.markdown("""<hr style="height:1px;border:none;color:black;background-color:black;" /> """,
            unsafe_allow_html=True)
c0,c1, c2 = st.columns((1, 12, 2))
with c1:

    st.markdown(f"<h3 style='text-align: center;color:black '> Regularize Scores </h1>", unsafe_allow_html=True)
with c2:
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    slider_toggle = st.toggle('',key=7)

    
#st.caption('This is a string that explains something above.')
c0,c1, c2,  c4,c5 = st.columns((3,10.2,  1, 2,1))
with c1:
    
    with st.expander(' _***Click to view more information about the scores***_ ', expanded=False):

            st.markdown(f"<h10 style='text-align: center;color:black '> Pannello dedicato alla regolarizzazione dei pesi per la creazione degli scores finali.", unsafe_allow_html=True)
            st.markdown("""<hr style="height:0.3px;border:none;color:black;background-color:black;" /> """,
            unsafe_allow_html=True)

            st.markdown(f"<h10 style='text-align: center;color:black '>:red[Sm]: Manager Score ( _Quanto è affine un articolo per il manager?_ ) . Calcolato mediante algoritmi di affinità tra manager e articoli testate", unsafe_allow_html=True)

            st.markdown(f"<h10 style='text-align: center;color:black '>:red[Sk]: Keywords Score- Calcolato mediante la lista keywords fornita da Eni )", unsafe_allow_html=True)
            st.markdown("""<hr style="height:0.3px;border:none;color:black;background-color:black;" /> """,
            unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>:red[Sv]: Virality Score ( _Come si posiziona un articolo in termini di viralità?_ ) - Calcolato mediante Virality Score gnews+Virality Score searchs(Sv1 + Sv2)", unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>:red[Sv1]: Virality Score gnews - Calcolato mediante le news in prima pagina nelle principali testate", unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>:red[Sv2]: Virality Score searchs - Calcolato mediante i principali trends di richerca sul web (Google - Wikipedia)", unsafe_allow_html=True)
            
            st.markdown("""<hr style="height:0.3px;border:none;color:black;background-color:black;" /> """,
            unsafe_allow_html=True)
            st.markdown(f"<h10 style='text-align: center;color:black '>📊:red[Advocacy Score]📊 Score finale calcolato mediante il rapporto tra Manager Score e Virality Score - Attualmente pesato di default per 0.7 Manager Score e 0.3 Virality Score ", unsafe_allow_html=True)
            
st.markdown("""<hr style="height:0.1px;border:none;color:black;background-color:black;" /> """,
            unsafe_allow_html=True)
c1, c2,c3 = st.columns((10, 0.5,10))

with c1:
    c1, c2 = st.columns((2, 10))
    with c2:
        st.markdown(f"<h6 style='text-align: right;color:black '>Manager Score </h1>", unsafe_allow_html=True, help='Quanto peso vuoi assegnare alle keywords fornite da Eni per il calcolo del Manager Score? ')

    
    num_score_1 = slider_scores(1,'Manager Score: 0','Keywords Score: 0','Sm','Sk','0.7','0.3',slider_toggle)
with c3:
    c1, c2 = st.columns((2, 10))
    with c2:
        st.markdown(f"<h6 style='text-align: right;color:black '>Virality Score </h1>", unsafe_allow_html=True, help='Nella creazione del Virality Score, come vuoi distribuire il rapporto tra lo score viralità derivato dalle news con quello derivante dai trend di ricerca degli utenti? ')
    num_score_2 =slider_scores(2,'Virality Score   \nNews: 0','Virality Score Searchs: 0','Sv1','Sv2','0.5','0.5',slider_toggle)

c1, c2 = st.columns((4.5, 10))
with c2:    
    st.markdown(f"<h5 style='text-align: right;color:black '>Advocacy Score </h1>", unsafe_allow_html=True, help='Seleziona la distribuzione dei pesi che ritieni ideale per definire lo score finale. _Quanto peso vuoi dare alla viralità?_')    
num_score_3 = slider_scores(3,'Manager Score: 0','Virality Score: 0','Sm','Sv','0.7','0.3',slider_toggle)


c1, c2,c3 = st.columns((1, 6,11))
with c1:

    on = st.toggle('',key=8)
with c2:
    st.markdown(f"<h7 style='text-align: right;color:grey '>: Button Scores </h1>", unsafe_allow_html=True, help='selezionando il bottone si rendono attive le modifiche agli scores')
with c3:
    st.markdown(f"<h5 style='text-align: center;color:black '>Report </h1>", unsafe_allow_html=True, help='Visualizzazione delle principali informazioni e ranking degli articoli ordinati per differenti scores')  

if on:
    st.write('Scores aggiornati!')
    df = regolarize_scores(df,num_score_1,num_score_2,num_score_3)
    selection, list_selections = dataframe_with_selections(df)
else:
    selection, list_selections = dataframe_with_selections(df)

df_xlsx = to_excel(df)
st.download_button(label='📥 Download Current Result',
                                data=df_xlsx ,
                                file_name= 'Report_Advocacy.xlsx')




if len(selection)>0:
 
    index = selection.tail(1).index
 
    dominio,testo,titolo,summary,url,source,Sm,Sv,Sa = get_values_news(df,index)
    st.markdown("""<hr style="height:2px;border:none;color:black;background-color:black;" /> """,
                unsafe_allow_html=True)
    
    
    c_b, c_t, c_tt = st.columns((1.2, 10, 1))
    with c_b:
        st.write('')
       
        if ('x' not in st.session_state.keys()):
            
            st.session_state['x'] = 0
           
            
        if st.button(":soon:"):
            try:
                st.session_state['x']=st.session_state['x']+1
                ix = st.session_state['x']            
                ix_new = list_selections[ix]  
            except:
                st.session_state['x'] = 0
                ix_new = list_selections[0]
               
         
        if st.button(":back:"):
            try:
                st.session_state['x']=st.session_state['x']-1
                ix = st.session_state['x']
                ix_new = int(list_selections[ix])

            except:
                st.session_state['x'] = len(list_selections)-1
                ix_new = list_selections[len(list_selections)-1]

        try:
            dominio,testo,titolo,summary,url,source,Sm,Sv,Sa = get_values_news(df,ix_new)
        except:
            pass
        
        
    with c_t:
        st.markdown(f"<h1 style='text-align: center;color:black '> Dettagli Articolo selezionato </h1>", unsafe_allow_html=True)
        
        if source == 'Sprinklr':
            st.markdown(
                        f"""<a style='display: block; text-align: center;color:black' href="{url}">Link Articolo 
                        """,
                        unsafe_allow_html=True,)
        
    
    st.markdown("""<hr style="height:2px;border:none;color:black;background-color:black;" /> """,
                unsafe_allow_html=True)
    
    modal = st.container()
    
    css='''
            [data-testid="metric-container"] {
                width: fit-content;
                margin: auto;
            }
            
            [data-testid="metric-container"] > div {
                width: fit-content;
                margin: auto;
                color:black;
                font-size: 200%
            }
            
            [data-testid="metric-container"] label {
                width: fit-content;
                margin: auto;
                color:red;
                font-size: 150%;
            }
            '''
   

    
    
    with modal:
        
        c1, c2, c3 = st.columns((1, 10, 1))
        with c2:
            c1_1, c2_1, c3_1 = st.columns((1, 10, 1))
            with c2_1:
                st.image(f'data/logo/newspapers/{dominio}.png')
            st.markdown(f"<h2 style='text-align: center;color:black '> {titolo} </h1>", unsafe_allow_html=True)
            st.markdown("""<hr style="height:2px;border:none;color:black;background-color:black;" /> """,unsafe_allow_html=True)
            st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
            
            st.markdown(f"<h4 style='text-align: center;color:black '> Scores </h1>", unsafe_allow_html=True)
            c1, c2, c3, c4, = st.columns((0.05, 1, 1,1))
            
            with c1:
                st.write('')

                

    
            with c2:
    
                
                # I usually dump any scripts at the bottom of the page to avoid adding unwanted blank lines
                st.write('')
                st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
                st.metric(label="Advocacy Score", value=Sa)
                
            with c3:
                st.write('')
                st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
                st.metric(label="Manager Score", value=Sm)
            with c4:
                st.write('')
                st.markdown(f'<style>{css}</style>',unsafe_allow_html=True)
                st.metric(label="Virality Score", value=Sv)
            st.markdown("""<hr style="height:2px;border:none;color:black;background-color:black;" /> """,
                unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center;color:black '> Snippet </h1>", unsafe_allow_html=True)
            stx.scrollableTextbox(summary,height=150,fontFamily='cursive',border=True)
            
            st.markdown("""<hr style="height:2px;border:none;color:black;background-color:black;" /> """,
                unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center;color:black '> Testo completo </h1>", unsafe_allow_html=True)
            stx.scrollableTextbox(testo,height=300,fontFamily='cursive',border=True)
         

        
        
        
st.markdown(
 """
<style>

/* Style containers */
[data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
    border: 5px groove black;background-color: white;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: rgba(28, 131, 225, 0.1);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: rgb(30, 103, 119);
   overflow-wrap: break-word;
}

/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   black-space: break-spaces;
   color: black;
   fontSize: 100px
}
</style>
"""
, unsafe_allow_html=True)        


