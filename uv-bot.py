import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import Paginator
import asyncio
import json
import requests
import base64
import re

intents = discord.Intents.default()
intents.messages = True  
intents.message_content = True  
intents.members = True
intents.presences = True


bot = commands.Bot(command_prefix='uv!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('/help｜ultraviolet [uv]'))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
        
@bot.event
async def on_message(message):
    if "y/n" in message.content:
        await message.add_reaction('⬆️')
        await message.add_reaction('⬇️')

    await bot.process_commands(message)


@bot.tree.command(name="say", description="Envoie un message personnalisé sur un salon textuel.")
@app_commands.describe(texte="Le message à envoyer", salon_textuel="Lien du salon textuel")
async def say(interaction: discord.Interaction, texte: str, salon_textuel: discord.TextChannel = None):
    if interaction.user.guild_permissions.administrator:
      if salon_textuel is not None:  
                await salon_textuel.send(texte)
                embed = discord.Embed(description=f"✅** Bravo!｜**" + "Message envoyé sur " + salon_textuel.jump_url , color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
      else:
            erreur = "Le salon textuel n'existe pas."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
            erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)        
        

@bot.tree.command(name="avatar",description="Affiche l'avatar d'un utilisateur.")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar")
async def avatar(interaction: discord.Interaction,  utilisateur: discord.Member ):
    embed = discord.Embed(title=f"Avatar de {utilisateur.display_name}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=utilisateur.avatar)
    
    download_link = f"[Lien de l'image]({utilisateur.avatar})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="profileavatar",description="Affiche l'avatar de profil d'un utilisateur.")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar")
async def profileavatar(interaction: discord.Interaction,  utilisateur: discord.Member ):
    embed = discord.Embed(title=f"Avatar de {utilisateur.display_name}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=utilisateur.display_avatar)
    
    download_link = f"[Lien de l'image]({utilisateur.display_avatar})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="servericon",description="Affiche l'icône du serveur actuel.")
async def servericon(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    guild = bot.get_guild(guild_id)
    embed = discord.Embed(title=f"Icône du serveur {guild}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=guild.icon.url)
    download_link = f"[Lien de l'image]({guild.icon})"
    embed.add_field(name="", value=download_link)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help",description="Affiche des informations concernant [uv]bot.")
async def help(interaction: discord.Interaction):
 
    embed = discord.Embed(title="[uv]bot", description="[uv]bot est un bot discord crée exclusivement pour le serveur ultraviolet et présente de nombreuses fonctionnalitées essentielles. \n\n La liste des commandes et fonctionnalitées est affiché sur le projet Github.", color=discord.Color.from_rgb(193,168,233))
    view = discord.ui.View() 
    style = discord.ButtonStyle.grey 
    item = discord.ui.Button(style=style, label="Github", url="https://github.com/dxnuv/uv-bot")  
    view.add_item(item=item)
    await interaction.response.send_message(embed=embed,view=view)


    
@bot.tree.command(name="loveletter",description="Dévoile l'amour que tu portes envers une personne de ce serveur.")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar", message="Le message que vous voulez envoyer à votre cutie lover", anonyme="Afichage (ou non) de votre pseudo")
async def loveletter(interaction: discord.Interaction, utilisateur: discord.Member , message: str, anonyme: bool = False):
    guild_id = interaction.guild_id
    guild = bot.get_guild(guild_id)
    
    embed = discord.Embed(title=f"💌 Un membre du serveur {guild} vous a envoyé une lettre d'amour...", color=discord.Color.from_rgb(242, 80, 83))
    embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Cher,", value=utilisateur.mention, inline=False)
    embed.add_field(name="Message :", value=message, inline=False)
    if anonyme:
        embed.add_field(name="Signé, ", value="pookie bear anonyme 🥰")
    else:
        embed.add_field(name="Signé, ", value=interaction.user.mention + " 🥰")
        await utilisateur.send(embed=embed)
        embed = discord.Embed(description=f"✅** Bravo!｜**" + "💌 Lettre d'amour envoyé à " + utilisateur.mention , color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
@bot.tree.command(name="archive", description="Archive un salon textuel.")
@app_commands.describe(salon_textuel="Lien du salon textuel")
async def archive(interaction: discord.Interaction, salon_textuel: discord.TextChannel):

    if interaction.user.guild_permissions.administrator:
         date_formattee = datetime.now().strftime("%d-%m-%y")
         nom_salon_archives = f"{salon_textuel.name}-{date_formattee}"  
         categorie_archives = discord.utils.get(interaction.guild.categories, name="📦 archives")

         if categorie_archives is None:
             erreur = "La catégorie '📦 archives' n'a pas été trouvée."
             embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
             await interaction.response.send_message(embed=embed, ephemeral=True)
         else:
             await salon_textuel.edit(category=categorie_archives)

             salon_textuel_og = salon_textuel.name
             await salon_textuel.edit(name=nom_salon_archives)

             await salon_textuel.edit(position=0)

             embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel `{salon_textuel_og}` a été archivé avec succès." , color=discord.Color.green())
             await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
            erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)

    
    
@bot.tree.command(name="lock",description="Désactive un salon textuel.")
@app_commands.describe(salon_textuel="Le salon que vous souhaitez désactiver")
async def lock(interaction: discord.Interaction, salon_textuel: discord.TextChannel = None):
     if interaction.user.guild_permissions.administrator:
          if salon_textuel is None:
                await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
                embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {interaction.channel.jump_url} a été désactivé avec succès." , color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
          else:
               await salon_textuel.set_permissions(interaction.guild.default_role, send_messages=False)
               embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {salon_textuel.jump_url} a été désactivé avec succès." , color=discord.Color.green())
               await interaction.response.send_message(embed=embed)


     else:
             erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
             embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
             await interaction.response.send_message(embed=embed, ephemeral=True)    

@bot.tree.command(name="unlock",description="Réactive un salon textuel désactivé.")
@app_commands.describe(salon_textuel="Le salon que vous souhaitez réactiver")
async def unlock(interaction: discord.Interaction, salon_textuel: discord.TextChannel = None):
     if interaction.user.guild_permissions.administrator:
          if salon_textuel is None:
                await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
                embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {interaction.channel.jump_url} a été réactivé avec succès." , color=discord.Color.green())
                await interaction.response.send_message(embed=embed)
          else:
               await salon_textuel.set_permissions(interaction.guild.default_role, send_messages=True)
               embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {salon_textuel.jump_url} a été réactivé avec succès." , color=discord.Color.green())
               await interaction.response.send_message(embed=embed)


     else:
             erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
             embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
             await interaction.response.send_message(embed=embed, ephemeral=True)    


@bot.tree.command(name="rename", description="Renomme un salon textuel.")
@app_commands.describe(salon_textuel="Lien du salon textuel", nouveau_nom="Nouveau nom du salon textuel")
async def rename(interaction: discord.Interaction, salon_textuel: discord.TextChannel, nouveau_nom: str):
    if interaction.user.guild_permissions.administrator:
        try:
            nom_actuel = salon_textuel.name
            if '｜' in nom_actuel:  # Vérification s'il y a des caractères spéciaux
                nom_actuel = nom_actuel.split('｜', 1)[-1]
                nouveau_nom_complet = f"{salon_textuel.name.split('｜', 1)[0]}｜{nouveau_nom}"
            else:
                nouveau_nom_complet = nouveau_nom
            await salon_textuel.edit(name=nouveau_nom_complet)
            embed = discord.Embed(description=f"✅** Bravo!｜** Le salon textuel `{nom_actuel}` a été renommé en `{nouveau_nom_complet}` avec succès.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            erreur = f"Une erreur s'est produite lors du renommage du salon textuel : {e}"
            embed = discord.Embed(description=f"❌** Erreur｜** {erreur}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
    else:
        erreur = "Vous n'avez pas les permissions requises pour exécuter cette commande."
        embed = discord.Embed(description=f"❌** Erreur｜** {erreur}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

def load_tags():
    try:
        with open('tags.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Le fichier tags.json n'a pas été trouvé.")
        return {}
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier tags.json : {e}")
        return {}

def save_tags(tags):
    with open('tags.json', 'w') as file:
        json.dump(tags, file, indent=4)

tag_group = app_commands.Group(name="tag", description="Commandes liés aux tags")

@tag_group.command(name="use", description="Utilise un tag enregistré.")
@app_commands.describe(tag_nom="Nom du tag")
async def use_tag(interaction: discord.Interaction, tag_nom: str):
    tags = load_tags()
    if tag_nom in tags:
        tag_data = tags[tag_nom]
        if tag_data["private"]:
            user_id = str(interaction.user.id)
            if user_id != tag_data["creator_id"]:
                embed = discord.Embed(description="❌ **Erreur｜** Vous n'êtes pas autorisé à utiliser ce tag privé.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed)
                return
        texte = tag_data["texte"]
        await interaction.response.send_message(texte)
    else:
        embed = discord.Embed( description="❌ **Erreur｜** Ce tag n'existe pas.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

@tag_group.command(name="new", description="Crée un nouveau tag.")
@app_commands.describe(tag_nom="Nom du tag", texte="Texte intégré au tag", privé="Tag accessible par tous (ou non)")
async def create_tag(interaction: discord.Interaction, tag_nom: str, texte: str, privé: bool = False):
    tags = load_tags()
    user_id = str(interaction.user.id)
    if tag_nom in tags:
        embed = discord.Embed(description=f"❌ **Erreur｜** Le tag `{tag_nom}` existe déjà.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    tags[tag_nom] = {"texte": texte, "creator_id": user_id, "private": privé}
    save_tags(tags)
    embed = discord.Embed(description=f"✅ **Bravo!｜** Le tag `{tag_nom}` a été créé avec succès !", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@tag_group.command(name="remove", description="Supprime un tag créé par vous.")
@app_commands.describe(tag_nom="Nom du tag")
async def remove_tag(interaction: discord.Interaction, tag_nom: str):
    tags = load_tags()
    user_id = str(interaction.user.id)
    
    if tag_nom not in tags:
        embed = discord.Embed(description="❌ **Erreur｜** Ce tag n'existe pas.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    if tags[tag_nom]["creator_id"] == user_id or interaction.user.guild_permissions.administrator:
        del tags[tag_nom]
        save_tags(tags)
        embed = discord.Embed(description=f"✅ **Bravo!｜** Le tag `{tag_nom}` a été supprimé avec succès !", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="❌ **Erreur｜** Vous n'êtes pas l'auteur de ce tag ou vous n'avez pas les permissions requises.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)

@tag_group.command(name="list", description="Affiche l'ensemble des tags.")
async def tag_list(interaction: discord.Interaction):
    tags = load_tags()
    if not tags:
        embed = discord.Embed(title="Liste des tags", description="Aucun tag n'a été créé 😔. Utilisez `/tag new` pour créer un nouveau tag.", color=discord.Color.from_rgb(193,168,233 ))
        await interaction.response.send_message(embed=embed)
        return
    
    sorted_tags = sorted(tags.items()) 
    pages = []
    page_content = ""
    tags_per_page = 5
    current_page = 1
    total_pages = (len(sorted_tags) - 1) // tags_per_page + 1
    
    for index, (tag_nom, data) in enumerate(sorted_tags, start=1):
        creator = interaction.guild.get_member(int(data["creator_id"]))
        if creator:
            creator_name = creator.display_name
        else:
            creator_name = "Utilisateur Inconnu"
        if data["private"]:
            lock_icon = f"`🔒 Privé ` "
        else:
            lock_icon = f"`🔓 Publique ` "
        page_content += f"**{tag_nom}**  {lock_icon}\n`Auteur` : {creator_name}\n\n"
        if index % tags_per_page == 0 or index == len(sorted_tags):
            pages.append(discord.Embed(title=f"Liste des tags ({current_page}/{total_pages})", description=page_content , color=discord.Color.from_rgb(193,168,233 )))
            page_content = ""
            current_page += 1
    
    paginator = Paginator.Simple()
    await paginator.start(interaction, pages=pages)

@bot.tree.command(name="customemoji", description="Affiche l'image d'un emoji personnalisé.")
@app_commands.describe(emoji_nom="Nom de l'emoji personnalisé")
async def custom_emoji(interaction: discord.Interaction, emoji_nom: str):

    emoji = discord.utils.get(interaction.guild.emojis, name=emoji_nom)
    if emoji is None:
        embed = discord.Embed(description=f"❌ **Erreur｜** L'emoji personnalisé `{emoji_nom}` n'a pas été trouvé.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return

    emoji_url = emoji.url

    embed = discord.Embed(title=f"Emoji personnalisé : `{emoji_nom}`", color=discord.Color.from_rgb(193, 168, 233))
    embed.set_image(url=emoji_url)
    download_link = f"[Lien de l'image]({emoji_url})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)
bot.tree.add_command(tag_group)

with open('config.json', encoding="utf-8", errors="ignore") as f:
    datatoken = json.load(f)
    token = datatoken["token"]

def change_profile_picture(token, image_path):
    try:
        # Remove quotes and leading/trailing whitespaces from the image path
        image_path = image_path.replace('"',"")
        image_path = image_path.replace("'","")
        image_path = image_path.strip()
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        headers = {
            "Authorization": f"Bot {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Content-Type": "application/json"
        }
        data = {
            "avatar": f"data:image/png;base64,{encoded_image}"
        }
        url = "https://discord.com/api/v9/users/@me"
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"An error occurred: {response.json()}")
            return

        print('Profile picture has been changed succesfully.')
    except Exception as e:
        print(f"An error occurred: {e}")

image_path = "images\icon_uv-gifpp.gif"
print("Profile picture found.")
change_profile_picture(token, image_path)
bot.run(token)

