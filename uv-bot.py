import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import traceback
import time
import Paginator
import asyncio
import json
import random
import requests
import base64
import re

intents = discord.Intents.default()
intents.messages = True  
intents.message_content = True  
intents.members = True
intents.presences = True
intents.guild_scheduled_events = True
intents.voice_states = True
intents.guilds = True
intents.guild_messages = True


bot = commands.Bot(command_prefix='uv!', intents=intents)
version = "1.1.0-Beta2 [300424]"

def load_orbs():
    try:
        with open('orbs.json', 'r') as file:
            orbs = json.load(file)
    except FileNotFoundError:
        orbs = {}
    return orbs

def save_orbs(orbs):
    with open('orbs.json', 'w') as file:
        json.dump(orbs, file, indent=4)

async def orbs_for_voice():
    await bot.wait_until_ready()
    while not bot.is_closed():
        orbs = load_orbs()
        for guild in bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    user_id = str(member.id)
                    if user_id in orbs:
                        orbs[user_id] += 0.01
                    else:
                        orbs[user_id] = 0.01
        save_orbs(orbs)
        await asyncio.sleep(60)  

    
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('/help｜ultraviolet [uv]'))
    bot.loop.create_task(orbs_for_voice())
    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            print("Le salon de logging existe.")
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")
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

@bot.event
async def on_message_delete(message):
    embed = discord.Embed(description=f"Message supprimé sur {message.channel.jump_url}", color=discord.Color.red())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar)
    embed.add_field(name="Auteur du message", value=f"{message.author} `({message.author.id})`", inline=False)
    embed.set_footer(text=f"ID : {message.id}")
    embed.add_field(name="Contenu du message", value=message.content if message.content else "Contenu inconnu", inline=False)
    
    send_time = f"<t:{int(message.created_at.timestamp())}:F>"
    embed.add_field(name="Date d'envoi", value=send_time, inline=False)
    
    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        embed = discord.Embed(description=f"Message modifié sur {after.channel.jump_url}", color=discord.Color.from_rgb(193,168,233))
        embed.set_author(name=after.author.display_name, icon_url=after.author.avatar)
        embed.add_field(name="Auteur du message", value=f"{after.author} `({after.author.id})`", inline=False)
        embed.set_footer(text=f"ID : {after.id}")
        embed.add_field(name="Nouveau contenu", value=after.content, inline=False)
        embed.add_field(name="Ancien contenu", value=before.content, inline=False)
        send_time = f"<t:{int(before.created_at.timestamp())}:F>"
        embed.add_field(name="Date d'envoi", value=send_time, inline=False)
        
        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_member_update(before, after):
    added_roles = set(after.roles) - set(before.roles)
    removed_roles = set(before.roles) - set(after.roles)
    if before.display_name != after.display_name:
        embed = discord.Embed(description=f"{after.mention} `({after.name})` a été mis à jour", color=discord.Color.from_rgb(193,168,233))
        embed.set_author(name=after.display_name, icon_url=after.avatar)
        embed.add_field(name="Nouveau pseudo", value=after.display_name, inline=False)
        embed.add_field(name="Ancien pseudo", value=before.display_name, inline=False)
        embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)
        embed.set_footer(text=f"ID : {after.id}")
        
        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

    if added_roles:
        for role in added_roles:
            embed = discord.Embed(description=f"{after.mention} a été attribué le rôle {role.mention}", color=discord.Color.green())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date de création", value=f"<t:{int(role.created_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")

    if removed_roles:
        for role in removed_roles:
            embed = discord.Embed(description=f"{after.mention} a été retiré le rôle {role.mention}", color=discord.Color.red())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date de création", value=f"<t:{int(role.created_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
    if before.timed_out_until is None:
        if after.timed_out_until is not None:
            embed = discord.Embed(description=f"{after.mention} a été exclu", color=discord.Color.red())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date d'expiration", value=f"<t:{int(after.timed_out_until.timestamp())}:F>", inline=False)
            embed.add_field(name="Date d'arrivée", value=f"<t:{int(after.joined_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
                
    if before.timed_out_until is not None:
        if after.timed_out_until is None:
            embed = discord.Embed(description=f"{after.mention} n'est plus exclu", color=discord.Color.green())
            embed.set_author(name=after.display_name, icon_url=after.avatar)
            embed.set_footer(text=f"ID : {after.id}")
            embed.add_field(name="Date d'arrivée", value=f"<t:{int(after.joined_at.timestamp())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            
@bot.event
async def on_guild_channel_update(before, after):
    if isinstance(after, discord.TextChannel) and before.overwrites != after.overwrites:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.overwrite_update): 
            if entry.target == after:
                embed = discord.Embed(description=f"Les permissions du salon {after.mention} ont été modifiées.", color=discord.Color.from_rgb(193,168,233))
                embed.set_footer(text=f"ID : {after.guild.id}")
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    if isinstance(before, discord.CategoryChannel) and before.overwrites != after.overwrites:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.overwrite_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Les permissions de la catégorie {after.mention} ont été modifiées.", color=discord.Color.from_rgb(193,168,233))
                embed.set_footer(text=f"ID : {after.guild.id}")
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    if before.name != after.name and isinstance(after, discord.TextChannel):
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Le salon {after.mention} a été renommé", color=discord.Color.from_rgb(193,168,233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                embed.add_field(name="Ancien nom", value=before.name, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    if before.name != after.name and isinstance(after, discord.VoiceChannel):
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Le salon {after.mention} a été renommé", color=discord.Color.from_rgb(193,168,233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                embed.add_field(name="Ancien nom", value=before.name, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    elif isinstance(after, discord.CategoryChannel) and before.name != after.name:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.channel_update):
            if entry.target == after:
                embed = discord.Embed(description=f"La catégorie {after.mention} a été renommée", color=discord.Color.from_rgb(193, 168, 233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.add_field(name="Nouveau nom", value=after.name, inline=False)
                embed.add_field(name="Ancien nom", value=before.name, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
@bot.event
async def on_user_update(before, after):
    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if before.avatar != after.avatar:
        embed = discord.Embed(description=f"{after.mention} `({after.name})` a mis à jour son profil", color=discord.Color.from_rgb(193, 168, 233))
        embed.set_author(name=after.name, icon_url=after.avatar.url)
        embed.set_thumbnail(url=after.avatar.url)
        download_link = f"[Lien de l'image]({after.avatar.url})"
        embed.add_field(name="", value=download_link)
        embed.set_footer(text=f"ID : {after.id}")
        embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)
        
        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_guild_update(before, after):
    if before.icon != after.icon:
        async for entry in after.audit_logs(action=discord.AuditLogAction.guild_update):
            if entry.target == after:
                embed = discord.Embed(description=f"Le serveur {after.name} a été mise à jour", color=discord.Color.from_rgb(193, 168, 233))
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {after.id}")
                embed.set_thumbnail(url=after.icon.url)
                download_link = f"[Lien de l'image]({after.icon.url})"
                embed.add_field(name="Nouvelle icône", value=download_link, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(after.created_at.timestamp())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    
    if before.name != after.name:
        async for entry in after.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            author = entry.user
            embed = discord.Embed(description=f"Le serveur {after.name} a été mise à jour", color=discord.Color.from_rgb(193, 168, 233))
            embed.set_thumbnail(url=after.icon.url)
            embed.set_author(name=author.display_name, icon_url=author.avatar)
            embed.set_footer(text=f"ID : {before.id}")
            embed.add_field(name="Nouveau nom", value=after.name, inline=False)
            embed.add_field(name="Ancien nom", value=before.name, inline=False)
            embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_channel_delete(channel):
    if not isinstance(channel, discord.CategoryChannel):
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                embed = discord.Embed(description=f"Le salon `{channel.name}` a été supprimé", color=discord.Color.red())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    else:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                embed = discord.Embed(description=f"La catégorie `{channel.name}` a été supprimée", color=discord.Color.red())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break

@bot.event
async def on_guild_channel_create(channel):
    if not isinstance(channel, discord.CategoryChannel):
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:
                category_name = "Aucune"
                category_position = "Aucune"
                if channel.category:
                    category_name = channel.category.name
                    category_position = channel.category.position
                embed = discord.Embed(description=f"Le salon {channel.mention} a été créé", color=discord.Color.green())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Catégorie", value=category_name, inline=False)
                embed.add_field(name="Emplacement", value=category_position, inline=False)
                embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break
    else:
        async for entry in channel.guild.audit_logs(action=discord.AuditLogAction.channel_create):
            if entry.target.id == channel.id:
                embed = discord.Embed(description=f"La catégorie `{channel.name}` a été créée", color=discord.Color.green())
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.set_footer(text=f"ID : {channel.id}")
                embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config()
                log_channel_id = config.get('log_channel')
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break

@bot.event
async def on_member_join(member):
    embed = discord.Embed(description=f"{member.mention} a rejoint le serveur", color=discord.Color.green())
    embed.set_author(name=member.display_name, icon_url=member.avatar)
    embed.set_footer(text=f"ID : {member.id}")
    embed.add_field(name="Date d'arrivée", value=f"<t:{int(time.time())}:F>", inline=False)
    embed.add_field(name="Date de création du compte", value=f"<t:{int(member.created_at.timestamp())}:F>", inline=False)
    embed.add_field(name="Nombre de membres", value=len(member.guild.members), inline=False)

    config = load_config()
    log_channel_id = config.get('log_channel')
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_member_remove(member):
    embed = discord.Embed(description=f"{member.mention} a quitté le serveur", color=discord.Color.red())
    embed.set_author(name=member.display_name, icon_url=member.avatar)
    embed.set_footer(text=f"ID : {member.id}")
    embed.add_field(name="Date de départ", value=f"<t:{int(time.time())}:F>", inline=False)
    embed.add_field(name="Date d'arrivée", value=f"<t:{int(member.joined_at.timestamp())}:F>", inline=False)

    config = load_config()
    log_channel_id = config.get('log_channel')
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
        if entry.target.id == user.id:
            embed = discord.Embed(description=f"{user.mention} a été banni du serveur", color=discord.Color.red())
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.set_footer(text=f"ID : {user.id}")
            embed.add_field(name="Raison du bannissement", value=entry.reason if entry.reason else "Aucune raison spécifiée", inline=False)
            embed.add_field(name="Date du bannissement", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_member_unban(guild, user):
    async for entry in guild.audit_logs(action=discord.AuditLogAction.unban):
        if entry.target.id == user.id:
            embed = discord.Embed(description=f"{user.mention} a été débanni du serveur", color=discord.Color.green())
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.set_footer(text=f"ID : {user.id}")
            embed.add_field(name="Date du débannissement", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config()
            log_channel_id = config.get('log_channel')
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_role_create(role):
    async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_create):
        if entry.target.id == role.id:
            embed = discord.Embed(description=f"Le rôle {role.mention} a été créé", color=discord.Color.green())
            embed.set_footer(text=f"ID du rôle : {role.id}")
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_role_delete(role):
    async for entry in role.guild.audit_logs(action=discord.AuditLogAction.role_delete):
        if entry.target.id == role.id:
            embed = discord.Embed(description=f"Le rôle `{role.name}` a été supprimé", color=discord.Color.red())
            embed.set_footer(text=f"ID du rôle : {role.id}")
            embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
            embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
            break

@bot.event
async def on_guild_role_update(before, after):
    changes = []
    if before.name != after.name:
        changes.append(f"Nom : {before.name} → {after.name}")
    if before.color != after.color:
        changes.append(f"Couleur : {before.color} → {after.color}")
    if before.permissions != after.permissions:
        changes.append("Permissions modifiées")

    if changes:
        async for entry in after.guild.audit_logs(action=discord.AuditLogAction.role_update):
            if entry.target.id == after.id:
                embed = discord.Embed(description=f"Le rôle {after.mention} a été modifié", color=discord.Color.from_rgb(193, 168, 233))
                embed.set_footer(text=f"ID du rôle : {after.id}")
                embed.set_author(name=entry.user.display_name, icon_url=entry.user.avatar)
                embed.add_field(name="Changements", value="\n".join(changes), inline=False)
                embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

                config = load_config() 
                log_channel_id = config.get('log_channel') 
                if log_channel_id:
                    log_channel = bot.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(embed=embed)
                    else:
                        print("Le salon de logging n'existe pas.")
                else:
                    print("Le salon de logging n'a pas été défini.")
                break

@bot.event
async def on_voice_state_update(member, before, after):
    
    if before.channel != after.channel:
        action = None
        if before.channel is None:
            action = "rejoint"
        elif after.channel is None:
            action = "quitté"
        else:
            action = "déplacé"
        if action == "déplacé":
            embed = discord.Embed(description=f"{member.mention} a été déplacé dans un autre salon vocal.", color=discord.Color.from_rgb(193,168,233))
            embed.set_footer(text=f"ID : {member.id}")
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.add_field(name="Salon vocal actuel", value=after.channel.jump_url if after.channel else "Aucun", inline=False)
            embed.add_field(name="Salon vocal précédent", value=before.channel.jump_url if before.channel else "Aucun", inline=False)
            embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")
    
    if before.mute != after.mute or before.deaf != after.deaf:
        action = None
        if before.mute != after.mute and after.mute:
            action = "rendu muet"
        elif before.deaf != after.deaf and after.deaf:
            action = "mis en sourdine"
        elif before.mute != after.mute and not after.mute:
            action = "n'est plus muet"
        elif before.deaf != after.deaf and not after.deaf:
            action = "n'est plus en sourdine"

        if action:
            if before.channel is None:
                channel = after.channel
            else:
                channel = before.channel

            if before.channel and before.channel.guild.me.guild_permissions.view_audit_log:
                mod = None
                async for entry in before.channel.guild.audit_logs(action=discord.AuditLogAction.member_update):
                    if entry and entry.target.id == member.id and entry.user.id != bot.user.id:
                        mod = entry.user
                        break
            else:
                mod = None
            embed = discord.Embed(description=f"Le statut vocal de {member.mention} a été mis à jour.", color=discord.Color.from_rgb(193,168,233))
            if mod:
                embed.set_footer(text=f"{mod.display_name} | ID : {member.id}", icon_url=mod.avatar.url)
            else:
                embed.set_footer(text=f"ID : {member.id}")
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.add_field(name="Action", value=action, inline=True)
            embed.add_field(name="Muet", value="Oui" if after.mute else "Non", inline=True)
            embed.add_field(name="Sourd", value="Oui" if after.deaf else "Non", inline=True)
            embed.add_field(name="Salon vocal", value=channel.jump_url, inline=True)
            embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

            config = load_config() 
            log_channel_id = config.get('log_channel') 
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(embed=embed)
                else:
                    print("Le salon de logging n'existe pas.")
            else:
                print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_scheduled_event_create(event):
    embed = discord.Embed(description=f"L'évenément `{event.name}` a été créé", color=discord.Color.green())
    embed.add_field(name="Description", value=event.description, inline=False)
    embed.add_field(name="Début", value=f"<t:{int(event.start_time.timestamp())}:F>" , inline=True)
    if event.end_time:
        embed.add_field(name="Fin", value=f"<t:{int(event.end_time.timestamp())}:F>", inline=True)
    if event.location:
        embed.add_field(name="Lieu", value=event.location, inline=False)
    if event.channel:
        embed.add_field(name="Salon", value=event.channel.jump_url, inline=False)
    embed.add_field(name="Date de création", value=f"<t:{int(time.time())}:F>", inline=False)
    if event.cover_image:
        embed.set_image(url=event.cover_image.url)
    
    creator = event.creator.display_name if event.creator else "Inconnu"
    creator_icon_url = event.creator.avatar.url if creator != "Inconnu" else discord.Embed.Empty
    embed.set_author(name=f"{creator}", icon_url=creator_icon_url)

    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_scheduled_event_delete(event):
    embed = discord.Embed(description=f"L'évenément `{event.name}` a été déprogrammé", color=discord.Color.red())
    embed.add_field(name="Description", value=event.description, inline=False)
    embed.add_field(name="Début", value=f"<t:{int(event.start_time.timestamp())}:F>" , inline=True)
    if event.end_time:
        embed.add_field(name="Fin", value=f"<t:{int(event.end_time.timestamp())}:F>", inline=True)
    if event.location:
        embed.add_field(name="Lieu", value=event.location, inline=False)
    if event.channel:
        embed.add_field(name="Salon", value=event.channel.jump_url, inline=False)
    embed.add_field(name="Date de suppression", value=f"<t:{int(time.time())}:F>", inline=False)
    if event.cover_image:
        embed.set_image(url=event.cover_image.url)
    
    creator = event.creator.display_name if event.creator else "Inconnu"
    creator_icon_url = event.creator.avatar.url if creator != "Inconnu" else discord.Embed.Empty
    embed.set_author(name=f"{creator}", icon_url=creator_icon_url)

    config = load_config() 
    log_channel_id = config.get('log_channel') 
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print("Le salon de logging n'existe pas.")
    else:
        print("Le salon de logging n'a pas été défini.")

@bot.event
async def on_scheduled_event_update(before, after):
    changes = []
    if before.name != after.name:
        changes.append(f"Nom : {before.name} → {after.name}")
    if before.start_time != after.start_time:
        changes.append(f"Début : <t:{int(before.start_time.timestamp())}:F> → <t:{int(after.start_time.timestamp())}:F>"     )
    if before.end_time != after.end_time:
        changes.append(f"Fin : <t:{int(before.end_time.timestamp())}:F> → <t:{int(after.end_time.timestamp())}:F>"     )
    if before.description != after.description:
        changes.append(f"Description : {before.description} → {after.description}")
    if before.location != after.location:
        changes.append(f"Lieu : {before.location} → {after.location}")
    if before.cover_image != after.cover_image:
        changes.append("Image modifiée")
    if changes:
        embed = discord.Embed(description=f"L' événement `{after.name}` a été mis à jour", color=discord.Color.from_rgb(193, 168, 233))
        embed.set_footer(text=f"ID : {after.id}")
        
        updater_name = after.creator.display_name if after.creator else "Inconnu"
        updater_avatar_url = after.creator.avatar.url if updater_name != "Inconnu" else discord.Embed.Empty
        embed.set_author(name=f"{updater_name}", icon_url=updater_avatar_url)
        if after.cover_image:
            embed.set_image(url=after.cover_image.url)
        embed.add_field(name="Changements", value="\n".join(changes), inline=False)
        embed.add_field(name="Date de modification", value=f"<t:{int(time.time())}:F>", inline=False)

        config = load_config() 
        log_channel_id = config.get('log_channel') 
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)
            else:
                print("Le salon de logging n'existe pas.")
        else:
            print("Le salon de logging n'a pas été défini.")

@bot.tree.command(name="say", description="Envoie un message personnalisé sur un salon textuel")
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

@bot.tree.command(name="avatar",description="Affiche l'avatar d'un utilisateur")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar")
async def avatar(interaction: discord.Interaction,  utilisateur: discord.Member ):
    embed = discord.Embed(title=f"Avatar de {utilisateur.display_name}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=utilisateur.avatar)
    
    download_link = f"[Lien de l'image]({utilisateur.avatar})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="profileavatar",description="Affiche l'avatar de profil d'un utilisateur")
@app_commands.describe(utilisateur="L'utilisateur dont vous voulez connaitre l'avatar")
async def profileavatar(interaction: discord.Interaction,  utilisateur: discord.Member ):
    embed = discord.Embed(title=f"Avatar de {utilisateur.display_name}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=utilisateur.display_avatar)
    
    download_link = f"[Lien de l'image]({utilisateur.display_avatar})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="servericon",description="Affiche l'icône du serveur actuel")
async def servericon(interaction: discord.Interaction):
    guild_id = interaction.guild_id
    guild = bot.get_guild(guild_id)
    embed = discord.Embed(title=f"Icône du serveur {guild}",  color=discord.Color.from_rgb(193,168,233) )
    embed.set_image(url=guild.icon.url)
    download_link = f"[Lien de l'image]({guild.icon})"
    embed.add_field(name="", value=download_link)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help",description="Affiche des informations concernant [uv]bot")
async def help(interaction: discord.Interaction):
 
    embed = discord.Embed(title="[uv]bot", description="[uv]bot est un bot discord crée exclusivement pour le serveur ultraviolet et présente de nombreuses fonctionnalitées essentielles.", color=discord.Color.from_rgb(193,168,233))
    embed.add_field(name=f"Version", value=f"{version}", inline=True)
    view = discord.ui.View() 
    style = discord.ButtonStyle.grey 
    item = discord.ui.Button(style=style, label="Github", url="https://github.com/dxnel/uv-bot")  
    view.add_item(item=item)
    await interaction.response.send_message(embed=embed,view=view)

@bot.tree.command(name="loveletter",description="Envoie une lettre d'amour à l'utilisateur de votre choix")
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
    
@bot.tree.command(name="archive", description="Archive un salon textuel")
@app_commands.describe(salon_textuel="Lien du salon textuel")
async def archive(interaction: discord.Interaction, salon_textuel: discord.TextChannel):

    if interaction.user.guild_permissions.administrator:
         date_formattee = datetime.now().strftime("%d-%m-%y")
         nom_salon_archives = f"{salon_textuel.name}-{date_formattee}"  
         categorie_archives = discord.utils.get(interaction.guild.categories, name="📦 ARCHIVES")

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
             await interaction.response.send_message(embed=embed)
    else:
            erreur = "Vous n'avez pas les permissions requises pour éxécuter cette commande."
            embed = discord.Embed(description=f"❌** Erreur｜**" + f"{erreur}" , color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
   
@bot.tree.command(name="lock",description="Désactive un salon textuel")
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

@bot.tree.command(name="unlock",description="Réactive un salon textuel désactivé")
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

@bot.tree.command(name="rename", description="Renomme un salon textuel")
@app_commands.describe(salon_textuel="Lien du salon textuel", nouveau_nom="Nouveau nom du salon textuel")
async def rename(interaction: discord.Interaction, salon_textuel: discord.TextChannel, nouveau_nom: str):
    if interaction.user.guild_permissions.administrator:
        try:
            nom_actuel = salon_textuel.name
            await salon_textuel.edit(name=nouveau_nom)
            embed = discord.Embed(description=f"✅** Bravo!｜** Le salon textuel `{nom_actuel}` a été renommé en `{nouveau_nom}` avec succès.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            erreur = f"Une erreur s'est produite lors du renommage du salon textuel : {e}"
            embed = discord.Embed(description=f"❌** Erreur｜** {erreur}", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        erreur = "Vous n'avez pas les permissions requises pour exécuter cette commande."
        embed = discord.Embed(description=f"❌** Erreur｜** {erreur}", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

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

@tag_group.command(name="use", description="Utilise un tag enregistré")
@app_commands.describe(tag_nom="Nom du tag")
async def use_tag(interaction: discord.Interaction, tag_nom: str):
    tags = load_tags()
    if tag_nom in tags:
        tag_data = tags[tag_nom]
        if tag_data["private"]:
            user_id = str(interaction.user.id)
            if user_id != tag_data["creator_id"]:
                embed = discord.Embed(description="❌ **Erreur｜** Vous n'êtes pas autorisé à utiliser ce tag privé.", color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)  
                return
        texte = tag_data["texte"]
        await interaction.response.send_message(texte, ephemeral=tag_data["private"])  
    else:
        embed = discord.Embed(description="❌ **Erreur｜** Ce tag n'existe pas.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)  

@tag_group.command(name="new", description="Crée un nouveau tag")
@app_commands.describe(tag_nom="Nom du tag", texte="Texte intégré au tag", privé="Tag accessible par tous (ou non)")
async def create_tag(interaction: discord.Interaction, tag_nom: str, texte: str, privé: bool = False):
    tags = load_tags()
    user_id = str(interaction.user.id)
    if tag_nom in tags:
        embed = discord.Embed(description=f"❌ **Erreur｜** Le tag `{tag_nom}` existe déjà.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    tags[tag_nom] = {"texte": texte, "creator_id": user_id, "private": privé}
    save_tags(tags)
    embed = discord.Embed(description=f"✅ **Bravo!｜** Le tag `{tag_nom}` a été créé avec succès !", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@tag_group.command(name="remove", description="Supprime un tag créé par vous")
@app_commands.describe(tag_nom="Nom du tag")
async def remove_tag(interaction: discord.Interaction, tag_nom: str):
    tags = load_tags()
    user_id = str(interaction.user.id)
    
    if tag_nom not in tags:
        embed = discord.Embed(description="❌ **Erreur｜** Ce tag n'existe pas.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    if tags[tag_nom]["creator_id"] == user_id or interaction.user.guild_permissions.administrator:
        del tags[tag_nom]
        save_tags(tags)
        embed = discord.Embed(description=f"✅ **Bravo!｜** Le tag `{tag_nom}` a été supprimé avec succès !", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(description="❌ **Erreur｜** Vous n'êtes pas l'auteur de ce tag ou vous n'avez pas les permissions requises.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

@tag_group.command(name="list", description="Affiche l'ensemble des tags")
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
            pages.append(discord.Embed(title=f"Liste des tags ({current_page}/{total_pages})", description=page_content , color=discord.Color.from_rgb(193,168,233 ), ))
            page_content = ""
            current_page += 1
    
    paginator = Paginator.Simple()
    await paginator.start(interaction, pages=pages)

@bot.tree.command(name="customemoji", description="Affiche l'image d'un emoji personnalisé")
@app_commands.describe(emoji_nom="Nom de l'emoji personnalisé")
async def custom_emoji(interaction: discord.Interaction, emoji_nom: str):
    emoji = discord.utils.get(interaction.guild.emojis, name=emoji_nom)
    if emoji is None:
        embed = discord.Embed(description=f"❌ **Erreur｜** L'emoji personnalisé `{emoji_nom}` n'a pas été trouvé.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    emoji_url = emoji.url

    embed = discord.Embed(title=f"Emoji personnalisé : `{emoji_nom}`", color=discord.Color.from_rgb(193, 168, 233))
    embed.set_image(url=emoji_url)
    download_link = f"[Lien de l'image]({emoji_url})"
    embed.add_field(name="", value=download_link)
    await interaction.response.send_message(embed=embed)

bot.tree.add_command(tag_group)

def change_profile_picture(token, image_path):
    try:
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

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Le fichier config.json n'a pas été trouvé.")
        return {}
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier config.json : {e}")
        return {}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

log_group = app_commands.Group(name="log", description="Commandes liés aux logs")
bot.tree.add_command(log_group)

@log_group.command(name="set", description="Définit un salon de logging")
@app_commands.describe(salon_textuel="Lien du salon choisi")
async def set_log_channel(interaction: discord.Interaction, salon_textuel: discord.TextChannel):

    log_channel = salon_textuel.id
    config = load_config()
    config['log_channel'] = log_channel
    save_config(config)
    embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le salon textuel {salon_textuel.jump_url} a été défini comme salon de logging avec succès." , color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

orb_group = app_commands.Group(name="orb", description="Commandes liés aux orbes")
bot.tree.add_command(orb_group)

@orb_group.command(name="leaderboard", description="Affiche le classement des membres selon leur nombre d'orbes (points)")
async def orbs_list(interaction: discord.Interaction):
    orbs = load_orbs()
    if not orbs:
        embed = discord.Embed(title="Classement des orbes [uv]", description="Aucune orbe n'a été gagné 😔.", color=discord.Color.from_rgb(193, 168, 233))
        await interaction.response.send_message(embed=embed)
        return

    sorted_orbs = sorted(orbs.items(), key=lambda x: x[1], reverse=True)  # Tri en fonction du nombre d'orbes, du plus grand au plus petit

    pages = []
    page_content = ""
    users_per_page = 5
    current_page = 1
    total_pages = (len(sorted_orbs) - 1) // users_per_page + 1

    for index, (user_id, orbs_count) in enumerate(sorted_orbs, start=1):
        user = interaction.guild.get_member(int(user_id))
        if user:
            user_name = user.display_name
        else:
            user_name = "Utilisateur Inconnu"
        page_content += f"**{user_name}** : {round(orbs_count, 3)} <:uvbotorbe:1233831689470607360> \n\n"

        if index % users_per_page == 0 or index == len(sorted_orbs):
            pages.append(discord.Embed(title=f"Classement des orbes [uv] ({current_page}/{total_pages})", description=page_content, color=discord.Color.from_rgb(193, 168, 233)))
            page_content = ""
            current_page += 1

    paginator = Paginator.Simple()
    await paginator.start(interaction, pages=pages)


def load_shop():
    with open('shop.json', 'r', encoding='utf-8') as file:
        shop_content = file.read()
        shop_data = json.loads(shop_content)
        shop_items = shop_data.get('items', [])
    return shop_items

@orb_group.command(name="shop", description="Affiche la liste des objets disponibles dans le magasin")
async def shop(interaction: discord.Interaction):
    shop_items = load_shop()
    if not shop_items:
        embed = discord.Embed(title="Magasin", description="Aucun objet n'est en vente au shop 😔.", color=discord.Color.from_rgb(193, 168, 233))
        await interaction.response.send_message(embed=embed)
        return

    sorted_items = sorted(shop_items, key=lambda x: x['price'], reverse=True)

    pages = []
    page_content = ""
    items_per_page = 3
    current_page = 1
    total_pages = (len(sorted_items) - 1) // items_per_page + 1

    for index, item in enumerate(sorted_items, start=1):
        page_content += f"**{item['emoji']} {item['name']}**\n **Prix :** {item['price']} <:uvbotorbe:1233831689470607360>\n **Tag :** `{item['tag']}`\n{item['description']}\n\n"
        if index % items_per_page == 0 or index == len(sorted_items):
            embed = discord.Embed(title=f"Magasin ({current_page}/{total_pages})", description=page_content, color=discord.Color.from_rgb(193, 168, 233))
            embed.set_footer(text="La commande /orb buy [objet_tag] permet l'achat d'un objet.")
            pages.append(embed)
            page_content = ""
            current_page += 1

    paginator = Paginator.Simple()
    await paginator.start(interaction, pages=pages)


class CustomRole(discord.ui.Modal, title='Rôle Personnalisé'):

    name = discord.ui.TextInput(
        label='Nom du rôle',
        placeholder='Quoicoubeh...',
        required=True,
        max_length=20,
    )

    async def on_submit(self, interaction: discord.Interaction):

        guild = interaction.guild
        role_name = self.name.value
        role = await guild.create_role(name=role_name,color=discord.Color.from_rgb(193, 168, 233),hoist=True)

        await interaction.user.add_roles(role)

        embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Le rôle {role.mention} a été créé avec succès et attribué à {interaction.user.mention} !" , color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        embed = discord.Embed(description=f"❌ **Erreur｜** Une erreur inconnue est survenue.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)

class SendMsgAn(discord.ui.Modal, title='Message à envoyer'):

    text = discord.ui.TextInput(
        label='Texte',
        placeholder='puceau moi ? serieusement ^^ haha on me l avait pas sortie celle la depuis loooongtemps :)',
        required=True,
        max_length=300,
        style=discord.TextStyle.long,
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = bot.get_channel(1142786171441786910)
        embed_an = discord.Embed(title=f"😎 Un membre du serveur a quelque-chose à dire...", color=discord.Color.from_rgb(193, 168, 233))
        embed_an.set_thumbnail(url=interaction.user.avatar)
        embed_an.add_field(name="Message :", value=f"{self.text.value}", inline=False)
        embed_an.add_field(name="Signé, ", value=interaction.user.mention + " 🥰")
        embed_an.set_footer(text="Tu veux envoyer un message super swag comme celui-là? Utilise la commande /orb buy pour acheter ce produit")
        await channel.send(embed=embed_an)

        embed = discord.Embed(description=f"✅** Bravo!｜**" + "Message envoyé sur " + channel.jump_url , color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        embed = discord.Embed(description=f"❌ **Erreur｜** Une erreur inconnue est survenue.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

        traceback.print_exception(type(error), error, error.__traceback__)

@orb_group.command(name="me", description="Obtient le nombre d'orbes d'un utilisateur")
@app_commands.describe(utilisateur="Utilisateur dont vous voulez connaître le nombre d'orbes")
async def orbme(interaction: discord.Interaction, utilisateur: discord.Member = None):
    if utilisateur is None:

        user_id = str(interaction.user.id)
        orbs = load_orbs()
        if user_id in orbs:
            embed = discord.Embed(description=f"**{interaction.user.display_name}** : {round(orbs[user_id],3)} <:uvbotorbe:1233831689470607360> ", color=discord.Color.from_rgb(193, 168, 233))
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description=f"❌ **Erreur｜** Vous n'avez aucune orbe.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:

        user_id = str(utilisateur.id)
        orbs = load_orbs()
        if user_id in orbs:
             embed = discord.Embed(title=f"**{utilisateur.display_name}** : {round(orbs[user_id])} <:uvbotorbe:1233831689470607360> ", color=discord.Color.from_rgb(193, 168, 233))
             await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description=f"❌ **Erreur｜** Cet utilisateur n'a aucune orbe.", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)


     

@orb_group.command(name="buy", description="Acheter un objet dans le magasin")
@app_commands.describe(objet_tag="Tag de l'objet à acheter")
async def buy_item(interaction: discord.Interaction, objet_tag: str):
    guild = interaction.guild
    shop_items = load_shop()
    
    target_item = None
    for item in shop_items:
        if item['tag'].lower() == objet_tag.lower():
            target_item = item
            break
    
    if target_item is None:
        embed = discord.Embed(description=f"❌ **Erreur｜** Cet objet n'est pas disponible dans le shop.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    orbs = load_orbs()
    user_id = str(interaction.user.id)
    if user_id not in orbs or orbs[user_id] < target_item['price']:
        embed = discord.Embed(description=f"❌ **Erreur｜** Vous n'avez pas assez d'orbes pour acheter cet objet.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    orbs[user_id] -= target_item['price']
    save_orbs(orbs)

    if target_item['tag'] == 'role-perso':
        await interaction.response.send_modal(CustomRole())
        embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Objet {target_item['name']} acheté avec succès", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)    

    if target_item['tag'] == 'annonce-message':
        await interaction.response.send_modal(SendMsgAn())
        embed = discord.Embed(description=f"✅** Bravo!｜**" + f"Objet {target_item['name']} acheté avec succès", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)  

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    orbs = load_orbs()
    user_id = str(message.author.id)
    
    if user_id in orbs:
        orbs[user_id] += 0.01
    else:
        orbs[user_id] = 0.01
    
    save_orbs(orbs)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None:
        return

    user_id = str(payload.user_id)

    orbs = load_orbs()

    if user_id in orbs:
        orbs[user_id] += 0.005
    else:
        orbs[user_id] = 0.005

    save_orbs(orbs)

game_group = app_commands.Group(name="game", description="Commandes liés aux jeux")
bot.tree.add_command(game_group)

@game_group.command(name="number-guessing", description="Devinez le nombre correct et remportez des orbes")
async def guess_number(interaction: discord.Interaction):

    correct_number = random.randint(1, 500)
    
    start_time = time.time()
    participants = []
    winner = None
    
    embed=discord.Embed(title="🎲 Jeu : deviner le nombre correct", description="Le but du jeu est de trouver le nombre correct entre **1** et **500** en moins de **20 secondes**! Le vainqueur reçoit un nombre d'orbes <:uvbotorbe:1233831689470607360> en fonction du temps pris pour trouver le nombre correct.", color=discord.Color.from_rgb(193, 168, 233))
    embed.add_field(name="Jeu générée par", value=f"{interaction.user.display_name}", inline=True)
    embed.set_footer(text="Ce jeu est pas fou? Les commandes /game permettent de jouer à une belle séléction de jeux super swag")
    await interaction.response.send_message(embed=embed)
    print(correct_number)

    def check(message):
        return message.author != bot.user and message.channel == interaction.channel and message.content.isdigit()

    while time.time() - start_time < 20:
            message = await bot.wait_for('message', check=check) 
            guess = int(message.content)

            if message.author.display_name not in participants:
                participants.append(message.author.display_name)

            if guess == correct_number:
                winner = message.author
                break
            elif guess < correct_number:
                embed=discord.Embed(description="⬆️ Le nombre à deviner est plus grand !", color=discord.Color.from_rgb(193, 168, 233))
                await interaction.channel.send(embed=embed)
            else:
                embed=discord.Embed(description="⬇️ Le nombre à deviner est plus petit !", color=discord.Color.from_rgb(193, 168, 233))
                await interaction.channel.send(embed=embed)

    if winner:
               embed = discord.Embed(title="😎 Fin du jeu!", description=f"{winner.mention} a trouvé le nombre correct **({correct_number})** !", color=discord.Color.from_rgb(193, 168, 233))
               embed.add_field(name="Vainqueur", value=f"{winner.mention}", inline=True)
               embed.add_field(name="Temps de jeu", value=f"{round(time.time() - start_time)} secondes", inline=True)
               embed.add_field(name="Participant(s)", value=f"{', '.join(participants)}", inline=True)

               if round(time.time() - start_time) < 10:
                  recom  = round(random.uniform(0.2, 0.7),3)
               elif round(time.time() - start_time) < 20:
                  recom  = round(random.uniform(0.05, 0.01),3)
               elif round(time.time() - start_time) < 30:
                  recom  = round(random.uniform(0.01, 0.03),3)
               print(recom)
               print(round(time.time() - start_time))
               embed.add_field(name="Récompense", value=f"{recom} <:uvbotorbe:1233831689470607360>", inline=True)

               winner_id = str(winner.id)
               orbs = load_orbs()
               if winner_id in orbs:
                 orbs[winner_id] += recom
               else:
                 orbs[winner_id] = recom
               save_orbs(orbs)

               embed.set_footer(text="Ce jeu est pas fou? Les commandes /game permettent de jouer à une belle séléction de jeux super swag")
               await interaction.channel.send(embed=embed)
    else:
      embed = discord.Embed(title="⏳ Fin du jeu!", description=f"Le temps de jeu a expiré. Personne n'a trouvé le bon nombre à temps 🥺 **({correct_number})**.", color=discord.Color.from_rgb(193, 168, 233))
      embed.add_field(name="Vainqueur", value="Aucun", inline=True)
      embed.add_field(name="Temps de jeu", value=f"{round(time.time() - start_time)} secondes", inline=True)
      embed.add_field(name="Participant(s)", value=f"{', '.join(participants)}", inline=True)
      embed.add_field(name="Récompense", value="Aucune", inline=True)
      embed.set_footer(text="Ce jeu est pas fou? Les commandes /game permettent de jouer à une belle séléction de jeux super swag")
      await interaction.channel.send(embed=embed)

config = load_config()
token = config['token']

image_path = "images\icon_uv-gifpp.gif"
print("Profile picture found.")
change_profile_picture(token, image_path)
bot.run(token)
