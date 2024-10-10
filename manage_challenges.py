import json
import customtkinter as ctk
from tkinter import messagebox


# Carregar os dados dos jogadores.
def load_data():
    with open('players_data.json', 'r', encoding='utf-8') as file:
        return json.load(file)
    

# Salvar os dados dos jogadores.
def save_data(data):
    with open('players_data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Adicionar um novo jogador.
def add_player(nick):
    data = load_data()

    if not any(player['nick'] == nick for player in data['players']):
        new_player = {
            "nick": nick,
            "completed_challenges": {},
            "points": 0
        }

        data['players'].append(new_player)
        save_data(data)
        update_player_nicks()

        messagebox.showinfo("Sucesso!", f"Jogador {nick} adicionado com sucesso!")

    else:
        messagebox.showinfo("Erro!", "Jogador já existe.")


# Atualizar a lista de nicks no ComboBox.
def update_player_nicks():
    data = load_data()
    nicks = [player['nick'] for player in data['players']]

    player_nick_combo.configure(values=nicks)

    if nicks:
        player_nick_combo.set(nicks[0])

    else:
        player_nick_combo.set("")


# Remover um jogador.
def remove_player(nick):
    data = load_data()
    data['players'] = [player for player in data['players'] if player['nick'] != nick]

    save_data(data)

    messagebox.showinfo("Sucesso!", f"Jogador {nick} removido com sucesso.")


# Adicionar um desafio de jogador.
def add_challenge_to_player(nick, mod, challenge):
    data = load_data()

    for player in data['players']:

        if player['nick'] == nick:

            if mod not in player['completed_challenges']:
                player['completed_challenges'][mod] = []

            if challenge in player['completed_challenges'][mod]:
                messagebox.showinfo("Erro!", "Desafio já completado.")

            else:
                player['completed_challenges'][mod].append(challenge)
                player['points'] += data['challenges'][mod][challenge]['pontos']
                save_data(data)

                messagebox.showinfo(
                    "Sucesso!", f"Desafio '{challenge}' do mod '{mod}' completado pelo jogador {nick}.")
                
            return
        
    messagebox.showinfo("Erro!", f"Jogador {nick} não encontrado.")


# Remover um desafio de jogador.
def remove_challenge_to_player(nick, mod, challenge):
    data = load_data()
    
    for player in data['players']:

        if player['nick'] != nick:
            messagebox.showinfo("Erro!", f"Jogador não encontrado.")

            return

        if mod in player['completed_challenges'] and challenge in player['completed_challenges'][mod]:
            del player['completed_challenges'][mod]
            player['points'] -= player['points']
            save_data(data)
        
            messagebox.showinfo("Sucesso!", f"Desafio '{challenge}' removido do player '{nick}'.")

        else:
            messagebox.showinfo("Erro!", "Desafio ou player não encontrado.")
            

# Listar desafios por mod.
def list_challenges():
    data = load_data()
    challenges_text = ""

    for mod, challenges in data['challenges'].items():
        challenges_text += f"{mod}:\n"

        for challenge, details in challenges.items():
            pontos = details.get('pontos', 0)
            challenges_text += f"   - {challenge}: ({pontos} pontos)\n"

    return challenges_text


# Login do administrador.
def admin_login(usarname, password):
    data = load_data()

    if usarname == data['admin']['username'] and password == data['admin']['password']:
        return True
    
    else:
        return False


# Criar a interface gráfica.
def create_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Gerenciador de Desafios")
    root.geometry("600x400")

    tab_control = ctk.CTkTabview(root)
    tab_control.pack(expand=1, fill='both')

    data = load_data()
    nicks = [player['nick'] for player in data['players']]
    mods = list(data['challenges'].keys())


    # Lista para manter o controle das abas adicionadas.
    added_tabs = []


    # Aba de Login do Administrador.
    login_tab = tab_control.add("Login Admin")
    added_tabs.append("Login Admin")


    ctk.CTkLabel(login_tab, text="Usuário:").grid(row=0, column=0, sticky='w')
    admin_user_entry = ctk.CTkEntry(login_tab)
    admin_user_entry.grid(row=0, column=1, sticky='ew')

    ctk.CTkLabel(login_tab, text="Senha:").grid(row=1, column=0, sticky='w')
    admin_pass_entry = ctk.CTkEntry(login_tab, show='*')
    admin_pass_entry.grid(row=1, column=1, sticky='ew')


    def on_admin_login():

        if admin_login(admin_user_entry.get(), admin_pass_entry.get()):

            if "Administradores" not in added_tabs:
                admin_tab = tab_control.add("Administradores")
                added_tabs.append("Administradores")


                ctk.CTkLabel(admin_tab, text="Nick do Jogador:").grid(row=0, column=0, sticky='w')
                admin_nick_entry = ctk.CTkEntry(admin_tab)
                admin_nick_entry.grid(row=0, column=1, sticky='ew')


                ctk.CTkLabel(admin_tab, text="Pontos:").grid(row=4, column=0, sticky='w')
                admin_points_entry = ctk.CTkEntry(admin_tab)
                admin_points_entry.grid(row=4, column=1, sticky='ew')
                

                def update_points():
                    selected_mod = admin_mod_entry.get()
                    selected_challenge = admin_challenge_entry.get()

                    if selected_mod and selected_challenge:
                        points = data['challenges'][selected_mod][selected_challenge]['pontos']
                        
                        admin_points_entry.delete(0, 'end')
                        admin_points_entry.insert(0, points)


                def admin_challenge_entry_selected(choice):
                    update_points()
                    return choice
                

                ctk.CTkLabel(admin_tab, text="Desafio:").grid(row=2, column=0, sticky='w')
                chall = list(data['challenges']["Minecraft Vanilla"].keys())
                admin_challenge_entry = ctk.CTkComboBox(
                    admin_tab, values=chall, command=admin_challenge_entry_selected)
                admin_challenge_entry.grid(row=2, column=1, sticky='ew')
                

                def update_challenges():
                    selected_mod = admin_mod_entry.get()

                    if selected_mod:
                        challenges = list(data['challenges'][selected_mod].keys())

                        admin_challenge_entry.configure(values=challenges)
                        admin_challenge_entry.set('')
                

                def admin_mod_entry_selected(choice):
                    update_challenges()
                    return choice
                

                ctk.CTkLabel(admin_tab, text="Mod:").grid(row=1, column=0, sticky='w')
                mods = list(data['challenges'].keys())
                admin_mod_entry = ctk.CTkComboBox(admin_tab, values=mods, command=admin_mod_entry_selected)
                admin_mod_entry.set(mods[0])
                update_challenges()
                admin_mod_entry.grid(row=1, column=1, sticky='ew')


                ctk.CTkButton(
                    admin_tab, text="Adicionar Jogador", command=lambda: add_player(
                        admin_nick_entry.get())).grid(row=5, column=0, sticky='ew')
                
                ctk.CTkButton(
                    admin_tab, text="Remover Jogador", command=lambda: remove_player(
                        admin_nick_entry.get())).grid(row=5, column=1, sticky='ew')
                
                ctk.CTkButton(
                    admin_tab, text="Adicionar Desafio", command=lambda: add_challenge_to_player(
                        admin_nick_entry.get(), admin_mod_entry.get(), admin_challenge_entry.get()
                    )).grid(row=6, column=0, sticky='ew')
                
                ctk.CTkButton(
                    admin_tab, text="Remover Desafio", command=lambda: remove_challenge_to_player(
                        admin_nick_entry.get(), admin_mod_entry.get(), admin_challenge_entry.get()
                    )).grid(row=6, column=1, sticky='ew')
                
                ctk.CTkButton(admin_tab, text="Listar Desafios", command=lambda: 
                              messagebox.showinfo("Desafios", list_challenges()
                    )).grid(row=7, column=0, columnspan=2, sticky='ew')
                

            tab_control.set("Administradores")


            if "Login Admin" in added_tabs:
                tab_control.delete("Login Admin")
                added_tabs.remove("Login Admin")

        else:
            messagebox.showinfo("Erro!", "Usuário ou senha incorretos.")


    ctk.CTkButton(
        login_tab, text="Login", command=on_admin_login
    ).grid(row=2, column=0, columnspan=2, sticky='ew')


    # Aba dos Jogadores.
    player_tab = tab_control.add("Jogadores")


    ctk.CTkLabel(player_tab, text="Nick do Jogador:").grid(row=0, column=0, sticky='w')
    global player_nick_combo
    player_nick_combo = ctk.CTkComboBox(player_tab, values=nicks)
    player_nick_combo.grid(row=0, column=1, sticky='ew')


    if nicks:
        player_nick_combo.set(nicks[0])

    else:
        player_nick_combo.set("")


    ctk.CTkLabel(player_tab, text="Mod:").grid(row=1, column=0, sticky='w')
    player_mod_combo = ctk.CTkComboBox(player_tab, values=mods)
    player_mod_combo.grid(row=1, column=1, sticky='ew')


    if mods:
        player_mod_combo.set(mods[0])

    else:
        player_mod_combo.set("")


    root.mainloop()


# Executar a interface gráfica.
create_gui()