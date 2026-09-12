import os
import sys
import time
import random
from typing import List, Dict, Any

# Verificação amigável da biblioteca 'rich'
try:
    from rich.console import Console, Group
    from rich.table import Table
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.text import Text
    from rich.align import Align
    from rich.layout import Layout
    from rich.prompt import Prompt, IntPrompt
    from rich.live import Live
    from rich import box
except ImportError:
    print("\n" + "=" * 65)
    print(" 📦 BIBLIOTECA NECESSÁRIA NÃO ENCONTRADA")
    print("=" * 65)
    print(" Para ver a mesa gráfica com animações fluidas e cartas em 3D,")
    print(" instale a biblioteca 'rich' executando no terminal:")
    print("\n    pip install rich\n")
    print("=" * 65)
    sys.exit(1)

console = Console()

# Habilita suporte a códigos de escape ANSI no Windows
if os.name == "nt":
    os.system("")

def ler_tecla() -> str:
    """
    Captura teclas em tempo real (sem precisar de ENTER adicional),
    suportando navegação fluida por setas cima/baixo e enter em Windows, Linux e macOS.
    """
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):  # Código prefixo de tecla especial no Windows
            ch2 = msvcrt.getch()
            if ch2 == b"H":
                return "UP"
            elif ch2 == b"P":
                return "DOWN"
            elif ch2 == b"K":
                return "LEFT"
            elif ch2 == b"M":
                return "RIGHT"
        elif ch in (b"\r", b"\n"):
            return "ENTER"
        elif ch == b"\x1b":
            return "ESC"
        elif ch == b"\x03":  # Ctrl+C
            sys.exit(0)
        return ch.decode(errors="ignore")
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        antigas_config = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "UP"
                    elif ch3 == "B":
                        return "DOWN"
                    elif ch3 == "C":
                        return "RIGHT"
                    elif ch3 == "D":
                        return "LEFT"
                return "ESC"
            elif ch in ("\r", "\n"):
                return "ENTER"
            elif ch == "\x03":  # Ctrl+C
                sys.exit(0)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, antigas_config)

# Ícones temáticos para cada elemento investigativo
ICONES = {
    # Suspeitos
    "Lógica": "🧠",
    "Silogismo": "📜",
    "Premissa": "🗝️",
    "Sofismo": "🎭",
    "Falácia": "🪞",
    "Retórica": "🗣️",
    # Armas do Crime
    "Implicação": "🏹",
    "Contraposição": "⚔️",
    "Bi implicação": "🔄",
    "Entimema": "🗡️",
    # Locais dos Fatos
    "Contingencia": "🎲",
    "Tautologia": "♾️",
    "Contradição": "💥",
    "Equivalência": "⚖️",
}

# Cartas oficiais do jogo
personagens = ["Lógica", "Silogismo", "Premissa", "Sofismo", "Falácia", "Retórica"]
armas = ["Implicação", "Contraposição", "Bi implicação", "Entimema"]
locais = ["Contingencia", "Tautologia", "Contradição", "Equivalência"]

# Cópia imutável para referência na montagem da mesa
TODOS_PERSONAGENS = list(personagens)
TODAS_ARMAS = list(armas)
TODOS_LOCAIS = list(locais)

# Solução do mistério (gerada aleatoriamente conforme as regras)
solucao = {
    "personagem": random.choice(personagens),
    "arma": random.choice(armas),
    "local": random.choice(locais)
}

# Remove as 3 cartas da solução das disponíveis para distribuição
personagens.remove(solucao["personagem"])
armas.remove(solucao["arma"])
locais.remove(solucao["local"])

def renderizar_micro_carta(nome: str, status: str = "oculta") -> Text:
    """
    Renderiza um card ultra-compacto de linha única.
    Cores luminosas de máximo contraste sobre o fundo preto do terminal.
    Mãos alheias nunca são expostas; apenas o status pericial do dossiê.
    """
    icone = ICONES.get(nome, "🃏")
    t = Text()

    if status == "oculta":
        t.append(" 🂠 [ ? ? ? ? ? ? ? ] ", style="bold bright_cyan")
    elif status == "mao":
        t.append(f" ✔ {icone} {nome:<13} ", style="bold bright_green")
    elif status == "pista":
        t.append(f" 💡 {icone} {nome:<13} ", style="bold bright_yellow")
    elif status == "crime":
        t.append(f" 🎯 {icone} {nome:<13} ", style="bold bright_yellow")
    elif status == "descartada":
        t.append(f" ✖ {icone} {nome:<13} ", style="bold bright_red")
    else:
        t.append(f" 👁 {icone} {nome:<13} ", style="bold bright_white")

    return t

def selecionar_com_setas(titulo: str, opcoes: List[str], icone_tipo: str = "🔍", cor: str = "bright_cyan") -> str:
    """
    Menu com navegação por setas (CIMA / BAIXO) e destaque luminoso de alto contraste.
    Todo o texto é exibido uniformemente na cor da categoria sem cortes.
    """
    if not opcoes:
        return ""

    indice_selecionado = 0
    total = len(opcoes)

    cor_borda = {
        "magenta": "bright_magenta",
        "red": "bright_red",
        "blue": "bright_cyan",
        "cyan": "bright_cyan",
        "yellow": "bright_yellow",
        "green": "bright_green"
    }.get(cor, cor)

    def gerar_painel_selecao(idx: int) -> Panel:
        tabela = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 1))
        tabela.add_column("Opção", justify="left")

        for i, opt in enumerate(opcoes):
            ico = ICONES.get(opt, "•")
            if i == idx:
                # Opção selecionada com cursor amarelo e texto integralmente na cor da categoria
                texto_linha = Text.from_markup(
                    f" [bold bright_yellow]❯❯[/bold bright_yellow] {ico}  [bold {cor_borda}]{opt:<18}[/bold {cor_borda}] [bold bright_green]◄ [ ENTER ][/bold bright_green]"
                )
            else:
                # Opções mantêm a cor temática da categoria por completo
                texto_linha = Text.from_markup(
                    f"    {ico}  [{cor_borda}]{opt:<18}[/{cor_borda}]"
                )
            tabela.add_row(texto_linha)

        rodape = Text.from_markup(
            f"\n[bold bright_white]Navegue com [/bold bright_white][bold {cor_borda}]▲ CIMA[/bold {cor_borda}][bold bright_white] e [/bold bright_white]"
            f"[bold {cor_borda}]▼ BAIXO[/bold {cor_borda}][bold bright_white] │ Pressione [/bold bright_white]"
            f"[bold bright_green][ ENTER ][/bold bright_green][bold bright_white] para confirmar[/bold bright_white]"
        )

        return Panel(
            Group(tabela, Align.center(rodape)),
            title=f"[bold {cor_borda}]{icone_tipo} ESCOLHA: {titulo.upper()} {icone_tipo}[/bold {cor_borda}]",
            border_style=cor_borda,
            box=box.ROUNDED,
            padding=(0, 1)
        )

    with Live(gerar_painel_selecao(indice_selecionado), console=console, refresh_per_second=24, transient=True) as live:
        while True:
            tecla = ler_tecla()

            if tecla == "UP":
                indice_selecionado = (indice_selecionado - 1) % total
                live.update(gerar_painel_selecao(indice_selecionado))
            elif tecla == "DOWN":
                indice_selecionado = (indice_selecionado + 1) % total
                live.update(gerar_painel_selecao(indice_selecionado))
            elif tecla == "ENTER":
                return opcoes[indice_selecionado]
            elif tecla.isdigit():
                val = int(tecla)
                if 1 <= val <= total:
                    return opcoes[val - 1]

def selecionar_acao_turno(pistas_restantes: int) -> str:
    """
    Apresenta o menu de ações do turno com setas de navegação.
    Todas as palavras mantêm integralmente sua cor temática do início ao fim.
    """
    acoes = [
        {"id": "p", "label": "Perguntar sobre Suspeito", "icone": "👤", "cor": "bright_magenta"},
        {"id": "a", "label": "Perguntar sobre Arma", "icone": "🗡️", "cor": "bright_red"},
        {"id": "l", "label": "Perguntar sobre Local", "icone": "🏛️", "cor": "bright_cyan"},
        {"id": "t", "label": f"Pedir Pista ao Radar ({pistas_restantes} restantes)", "icone": "📡", "cor": "bright_yellow"},
        {"id": "k", "label": "Formalizar Acusação Final (Risco de Eliminação!)", "icone": "⚖️", "cor": "bright_red"},
    ]

    idx = 0
    total = len(acoes)

    def gerar_painel_acao(sel: int) -> Panel:
        tabela = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 1))
        tabela.add_column("Opção", justify="left")

        for i, a in enumerate(acoes):
            if i == sel:
                # Opção selecionada: cursor e texto com a cor definida sem cortes
                linha_txt = Text.from_markup(
                    f" [bold bright_yellow]❯❯[/bold bright_yellow] {a['icone']} [bold {a['cor']}]{a['label']:<50}[/bold {a['cor']}] [bold bright_green]◄ [ ENTER ][/bold bright_green]"
                )
            else:
                # Opção não selecionada: texto 100% colorido com a cor definida
                linha_txt = Text.from_markup(
                    f"    {a['icone']} [bold {a['cor']}]{a['label']:<50}[/bold {a['cor']}]"
                )
            tabela.add_row(linha_txt)

        instrucoes = Text.from_markup(
            "\n[bold bright_white]Navegue com [bold bright_cyan]▲ CIMA[/bold bright_cyan] e [bold bright_cyan]▼ BAIXO[/bold bright_cyan] │ [bold bright_green][ ENTER ][/bold bright_green] para executar ação[/bold bright_white]"
        )

        return Panel(
            Group(tabela, Align.center(instrucoes)),
            title="[bold bright_yellow]⚡ SELEÇÃO DE AÇÃO DO TURNO ⚡[/bold bright_yellow]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(0, 1)
        )

    with Live(gerar_painel_acao(idx), console=console, refresh_per_second=24, transient=True) as live:
        while True:
            tecla = ler_tecla()
            if tecla == "UP":
                idx = (idx - 1) % total
                live.update(gerar_painel_acao(idx))
            elif tecla == "DOWN":
                idx = (idx + 1) % total
                live.update(gerar_painel_acao(idx))
            elif tecla == "ENTER":
                return acoes[idx]["id"]
            elif tecla.lower() in ("p", "a", "l", "t", "k"):
                return tecla.lower()

def animar_virada_de_carta(nome_carta: str, categoria: str = "Geral", status_final: str = "mao"):
    """
    Animação cinematográfica de rotação 3D da carta com cores de alto contraste.
    """
    icone = ICONES.get(nome_carta, "🃏")
    cor_cat = {"Suspeito": "bright_magenta", "Arma": "bright_red", "Local": "bright_cyan"}.get(categoria, "bright_yellow")

    quadros = [
        Text.from_markup(f"[{cor_cat}]╭──────────────╮\n│ ░ [DOSSIÊ] ░ │\n╰──────────────╯[/{cor_cat}]"),
        Text.from_markup("[bright_cyan] ╭────────────╮ \n │  ✦  25°  ✦  │ \n ╰────────────╯ [/bright_cyan]"),
        Text.from_markup("[bright_white]   ╭────────╮   \n   │  ✦55°✦ │   \n   ╰────────╯   [/bright_white]"),
        Text.from_markup("[bright_yellow]       ╭╮       \n       ││ ✨    \n       ╰╯       [/bright_yellow]"),
        Text.from_markup(f"[{cor_cat}]   ╭────────╮   \n   │ ✨ {icone}   │   \n   ╰────────╯   [/{cor_cat}]"),
        Text.from_markup(f"[bold {cor_cat}] ╭────────────╮ \n │ {icone} {nome_carta[:10]:<10} │ \n ╰────────────╯ [/bold {cor_cat}]"),
    ]

    with Live(console=console, refresh_per_second=24, transient=True) as live:
        for q in quadros:
            live.update(Align.center(Panel(
                q,
                title="[bold bright_yellow]♦ GIRO 3D ♦[/bold bright_yellow]",
                border_style="bright_yellow",
                box=box.ROUNDED,
                padding=(0, 1)
            )))
            time.sleep(0.065)

        carta_final = renderizar_micro_carta(nome_carta, status=status_final)
        live.update(Align.center(Panel(
            Align.center(carta_final),
            title="[bold bright_green]✔ EVIDÊNCIA FIXADA![/bold bright_green]",
            border_style="bright_green",
            box=box.HEAVY,
            padding=(0, 1)
        )))
        time.sleep(0.45)

def animar_distribuicao_cartas(jogadores_nomes: Dict[str, str], cartas_jogadores: Dict[str, List[str]]):
    """
    Animação compacta simulando o carteador distribuindo cada carta confidencial.
    """
    console.clear()
    total_cartas = sum(len(c) for c in cartas_jogadores.values())
    entregues = 0

    with Live(console=console, refresh_per_second=18, transient=True) as live:
        max_cartas = max(len(c) for c in cartas_jogadores.values())
        for rodada in range(max_cartas):
            for cod_j, nome in jogadores_nomes.items():
                if rodada < len(cartas_jogadores[cod_j]):
                    entregues += 1
                    pct = int((entregues / total_cartas) * 100)
                    barra_tamanho = 18
                    preenchido = int((entregues / total_cartas) * barra_tamanho)
                    barra = f"[bold bright_green]{'━' * preenchido}[/bold bright_green][bright_white]{'─' * (barra_tamanho - preenchido)}[/bright_white]"

                    visual_mesa = Text()
                    visual_mesa.append("🂠 [BARALHO CENTRAL DA LÓGICA]\n", style="bold bright_cyan")
                    visual_mesa.append("              ▼  distribuindo...\n", style="bold bright_yellow")
                    visual_mesa.append("  Detetive: ", style="bold bright_white")
                    visual_mesa.append(f"{nome.upper()} ", style="bold bright_magenta")
                    visual_mesa.append(f"(Carta {rodada + 1})\n", style="bold bright_white")
                    visual_mesa.append(f"  Progresso: [{barra}] {pct}%", style="bold bright_cyan")

                    live.update(Panel(
                        Align.center(visual_mesa),
                        title="[bold bright_yellow]♠ DISTRIBUIÇÃO DOS ÁLIBIS ♠[/bold bright_yellow]",
                        border_style="bright_cyan",
                        box=box.DOUBLE,
                        padding=(0, 1)
                    ))
                    time.sleep(0.06)

    time.sleep(0.2)

def animar_radar_pista(nome_jogador: str):
    """
    Animação de radar forense investigando arquivos do caso.
    """
    etapas = [
        ("📡 Varrendo banco de dados da Tautologia...", "bright_cyan"),
        ("🔍 Cruzando registros com premissas...", "bright_blue"),
        ("🗝️ Descriptografando documento confidencial...", "bright_yellow"),
        ("💡 Pista lógica isolada com sucesso!", "bright_green")
    ]
    spins = ["◐", "◓", "◑", "◒"]

    with Live(console=console, refresh_per_second=16, transient=True) as live:
        for texto, cor in etapas:
            for ciclo in range(3):
                icone_spin = spins[ciclo % len(spins)]
                tela = Text()
                tela.append(f"{icone_spin} {texto}\n", style=f"bold {cor}")
                tela.append(f"Operador: Detetive {nome_jogador.upper()}", style="bold bright_white")

                live.update(Panel(
                    Align.center(tela),
                    title="[bold bright_yellow]📡 RADAR DE PISTAS[/bold bright_yellow]",
                    border_style=cor,
                    box=box.ROUNDED,
                    padding=(0, 1)
                ))
                time.sleep(0.04)

def animar_roleta_acusacao(acusacao: Dict[str, str], sucesso: bool):
    """
    Roleta cinematográfica no Tribunal da Lógica até fixar a acusação.
    """
    with Live(console=console, refresh_per_second=20, transient=True) as live:
        for i in range(18):
            p_fake = random.choice(TODOS_PERSONAGENS)
            a_fake = random.choice(TODAS_ARMAS)
            l_fake = random.choice(TODOS_LOCAIS)

            delay = 0.03 + (i * 0.007)

            live.update(Panel(
                Align.center(
                    f"[bold yellow]⚖️ TRIBUNAL DA LÓGICA: JULGAMENTO ⚖️[/bold yellow]\n\n"
                    f" [ {ICONES[p_fake]} {p_fake.upper():<11} ]  "
                    f" [ {ICONES[a_fake]} {a_fake.upper():<11} ]  "
                    f" [ {ICONES[l_fake]} {l_fake.upper():<11} ]"
                ),
                border_style="red" if i % 2 == 0 else "yellow",
                box=box.HEAVY,
                padding=(0, 1)
            ))
            time.sleep(delay)

        live.update(Panel(
            Align.center(
                f"[bold bright_white]VEREDICTO FINAL SUBMETIDO:[/bold bright_white]\n\n"
                f"👤 Suspeito: [bold magenta]{acusacao['personagem']}[/bold magenta]  "
                f"🗡️ Arma: [bold red]{acusacao['arma']}[/bold red]  "
                f"🏛️ Local: [bold blue]{acusacao['local']}[/bold blue]\n\n"
                f"[bold bright_yellow]O JUIZ ESTÁ BATENDO O MARTELO...[/bold bright_yellow]"
            ),
            border_style="bold bright_white",
            box=box.DOUBLE,
            padding=(0, 1)
        ))
        time.sleep(1.0)

def animar_tela_vitoria(nome: str):
    """Tela de vitória dedutiva."""
    simbolos = ["✨", "🎉", "🏆", "🌟", "💡", "🧠"]
    with Live(console=console, refresh_per_second=12, transient=True) as live:
        for _ in range(10):
            faixa = " ".join([random.choice(simbolos) for _ in range(10)])
            live.update(Panel(
                Align.center(
                    f"[bold yellow]{faixa}[/bold yellow]\n\n"
                    f"[bold bright_green]🏆 V I T Ó R I A   A B S O L U T A ! 🏆[/bold bright_green]\n\n"
                    f"[bold white]Parabéns, Detetive {nome.upper()}![/bold white]\n"
                    f"[cyan]Seu raciocínio desvendou o crime com precisão impecável![/cyan]\n\n"
                    f"[bold yellow]{faixa}[/bold yellow]"
                ),
                border_style="bold bright_green",
                box=box.DOUBLE,
                padding=(0, 1)
            ))
            time.sleep(0.1)

def animar_tela_derrota():
    """Tela de erro na acusação e eliminação."""
    with Live(console=console, refresh_per_second=8, transient=True) as live:
        for i in range(5):
            cor = "bold white on red" if i % 2 == 0 else "bold red on black"
            live.update(Panel(
                Align.center(
                    f"[{cor}] 💀 FALÁCIA DETECTADA! VOCÊ FOI ELIMINADO! 💀 [/{cor}]\n\n"
                    f"[bold white]Sua acusação continha premissas falsas.[/bold white]\n"
                    f"[dim red]Sua licença investigativa foi revogada nesta partida.[/dim red]"
                ),
                border_style="red",
                box=box.HEAVY,
                padding=(0, 1)
            ))
            time.sleep(0.2)

def animar_perda_de_vida(nome: str, vidas_restantes: int):
    """Animação de penalidade de vida perdida por dedução falha."""
    coracoes = "❤️ " * vidas_restantes + "🖤 " * (3 - vidas_restantes)
    with Live(console=console, refresh_per_second=10, transient=True) as live:
        for i in range(4):
            cor = "bold bright_red" if i % 2 == 0 else "bold bright_yellow"
            live.update(Panel(
                Align.center(
                    f"[{cor}]⚡ FALÁCIA DETECTADA! PREMISSA INCORRETA! ⚡[/{cor}]\n\n"
                    f"[bright_white]Detetive [/bright_white][bold bright_cyan]{nome.upper()}[/bold bright_cyan]"
                    f"[bright_white], sua acusação falhou e você perdeu 1 vida![/bright_white]\n\n"
                    f"[bold bright_red]Vidas Restantes: {coracoes.strip()} ({vidas_restantes}/3)[/bold bright_red]"
                ),
                border_style="bright_red",
                box=box.HEAVY,
                padding=(0, 1)
            ))
            time.sleep(0.25)
    time.sleep(0.5)

def animar_briefing_regras():
    """
    Apresentação das regras e explicação clara de por que os jogadores já começam com cartas.
    Cores em alto contraste otimizadas para fundos escuros.
    """
    console.clear()

    slides = [
        {
            "titulo": "FASE 1: O CRIME INTELECTUAL",
            "cor": "bright_red",
            "icone": "🏛️",
            "conteudo": (
                "[bold bright_red]ALERTA GERAL: A LÓGICA FORMAL FOI ASSASSINADA![/bold bright_red]\n\n"
                "• [bold bright_magenta]6 Suspeitos:[/bold bright_magenta] [bright_white]Lógica, Silogismo, Premissa, Sofismo, Falácia e Retórica.[/bright_white]\n"
                "• [bold bright_red]4 Armas:[/bold bright_red] [bright_white]Implicação, Contraposição, Bi implicação e Entimema.[/bright_white]\n"
                "• [bold bright_cyan]4 Locais:[/bold bright_cyan] [bright_white]Contingencia, Tautologia, Contradição e Equivalência.[/bright_white]\n\n"
                "[bold bright_yellow]1 Suspeito, 1 Arma e 1 Local[/bold bright_yellow] [bright_white]estão guardados no Envelope Secreto.[/bright_white]"
            )
        },
        {
            "titulo": "FASE 2: DISTRIBUIÇÃO TOTAL E ENVELOPE SECRETO",
            "cor": "bright_green",
            "icone": "🃏",
            "conteudo": (
                "[bold bright_green]A REGRA MATEMÁTICA DE DISTRIBUIÇÃO:[/bold bright_green]\n\n"
                "• [bright_white]Existem [/bright_white][bold bright_white]14 cartas no total[/bold bright_white].\n"
                "• [bold bright_yellow]Exatamente 1 carta de cada categoria[/bold bright_yellow] [bright_white](1 Suspeito, 1 Arma, 1 Local)\n"
                "  foi selada no Envelope do Crime: [/bright_white][bold bright_red]as 3 únicas cartas escondidas do jogo![/bold bright_red]\n"
                "• [bold bright_green]Todas as 11 cartas restantes foram distribuídas integralmente entre os detetives![/bold bright_green]\n"
                "  [bright_white](A mão de cada jogador é 100% SECRETA e nunca é revelada aos demais).[/bright_white]\n\n"
                "[bold bright_yellow]⚡ COMO FUNCIONA A DEDUÇÃO AO INVESTIGAR? ⚡[/bold bright_yellow]\n"
                "• [bright_white]Ao averiguar uma evidência, a perícia analisa a existência de álibis nos autos:[/bright_white]\n"
                "  [bold bright_cyan]1. Se a evidência possui álibi comprovado:[/bold bright_cyan] [bright_white]Ela é anotada como inocente descartada (✖)![/bright_white]\n"
                "  [bold bright_red]2. Se NENHUM álibi foi localizado:[/bold bright_red] [bold bright_yellow]Ela entra em alerta de máxima suspeita do crime (🎯)![/bold bright_yellow]"
            )
        },
        {
            "titulo": "FASE 3: VIDAS, PRIVACIDADE E CONTROLES",
            "cor": "bright_yellow",
            "icone": "❤️",
            "conteudo": (
                "[bold bright_yellow]SISTEMA DE VIDAS E SIGILO INDIVIDUAL:[/bold bright_yellow]\n\n"
                "• [bold bright_red]3 Vidas por Detetive (❤️❤️❤️):[/bold bright_red] [bright_white]Errar uma acusação final consome 1 vida.[/bright_white]\n"
                "• [bold bright_cyan]Cortina de Privacidade:[/bold bright_cyan] [bright_white]Seu painel é 100% blindado contra os outros jogadores!\n"
                "  Antes de cada turno, a tela é bloqueada até que só você esteja olhando.[/bright_white]\n"
                "• [bold bright_cyan]▲ CIMA[/bold bright_cyan] [bright_white]e[/bright_white] [bold bright_cyan]▼ BAIXO[/bold bright_cyan] [bright_white]-> Navega entre opções com destaque luminoso.[/bright_white]\n"
                "• [bold bright_green][ ENTER ][/bold bright_green] [bright_white]-> Confirma a seleção.[/bright_white]\n"
                "• [bold bright_yellow]Radar de Pistas (T)[/bold bright_yellow] [bright_white]-> Investiga evidências em posse dos outros detetives.[/bright_white]"
            )
        }
    ]

    for i, slide in enumerate(slides):
        console.clear()
        corpo = Text.from_markup(slide["conteudo"])
        rodape = Text.from_markup(
            f"\n[bold bright_white]Slide {i+1}/{len(slides)} │ [/bold bright_white][bold bright_green][ENTER][/bold bright_green][bold bright_white] Avançar │ [/bold bright_white][bold bright_yellow][P][/bold bright_yellow][bold bright_white] Pular[/bold bright_white]"
        )

        painel = Panel(
            Align.center(Group(corpo, rodape)),
            title=f"[bold {slide['cor']}]{slide['icone']} {slide['titulo']} {slide['icone']}[/bold {slide['cor']}]",
            border_style=slide["cor"],
            box=box.DOUBLE,
            padding=(0, 2)
        )
        console.print(painel)

        escolha = Prompt.ask("", default="").lower().strip()
        if escolha == "p":
            break

def exibir_mesa_dinamica(nome_jogador: str, cartas_jogador: List[str], pistas_reveladas: List[str], cartas_descartadas: set, crimes_detectados: set, vidas: int = 3):
    """
    Monta o Quadro de Evidências em formato ultra-compacto.
    Alto contraste calibrado para terminais escuros/pretos com indicador de vidas.
    Totalmente confidencial: não expõe quem possui quais cartas.
    """
    console.clear()

    coracoes = "❤️ " * vidas + "🖤 " * (3 - vidas)

    # Barra superior de status com vidas e cartas
    cabecalho = Text()
    cabecalho.append("🏛️ DOSSIÊ DE EVIDÊNCIAS  ", style="bold bright_magenta")
    cabecalho.append("│ Detetive: ", style="bold bright_white")
    cabecalho.append(f"{nome_jogador.upper()} ", style="bold bright_yellow")
    cabecalho.append("│ Vidas: ", style="bold bright_white")
    cabecalho.append(f"{coracoes.strip()} ", style="bold bright_red")
    cabecalho.append("│ Álibis: ", style="bold bright_white")
    cabecalho.append(f"{len(cartas_jogador)} ", style="bold bright_green")
    cabecalho.append("│ Pistas: ", style="bold bright_white")
    cabecalho.append(f"{len(pistas_reveladas)}/3", style="bold bright_yellow")

    console.print(Panel(Align.center(cabecalho), border_style="bright_cyan", box=box.ROUNDED, padding=(0, 1)))

    # Tabela ultra-compacta com cabeçalhos e bordas nítidas
    mesa = Table(
        box=box.ROUNDED,
        header_style="bold bright_white on grey23",
        border_style="bright_cyan",
        expand=True,
        padding=(0, 0),
        show_edge=True
    )

    mesa.add_column("👤 SUSPEITOS (6)", justify="center", style="bright_magenta", ratio=1)
    mesa.add_column("🗡️ ARMAS DO CRIME (4)", justify="center", style="bright_red", ratio=1)
    mesa.add_column("🏛️ LOCAIS DOS FATOS (4)", justify="center", style="bright_cyan", ratio=1)

    max_linhas = max(len(TODOS_PERSONAGENS), len(TODAS_ARMAS), len(TODOS_LOCAIS))

    for i in range(max_linhas):
        linha_celulas = []
        for coluna in [TODOS_PERSONAGENS, TODAS_ARMAS, TODOS_LOCAIS]:
            if i < len(coluna):
                item = coluna[i]
                if item in cartas_jogador:
                    status = "mao"
                elif item in crimes_detectados:
                    status = "crime"
                elif item in pistas_reveladas:
                    status = "pista"
                elif item in cartas_descartadas:
                    status = "descartada"
                else:
                    status = "oculta"

                linha_celulas.append(renderizar_micro_carta(item, status))
            else:
                linha_celulas.append(Text(" ─ ", style="bold bright_white"))

        mesa.add_row(*linha_celulas)

    console.print(mesa)

def exibir_mao_do_jogador(cartas_jogador: List[str]):
    """
    Exibe os álibis que o jogador possui em texto verde brilhante de alto contraste.
    """
    badges = []
    for carta in cartas_jogador:
        icone = ICONES.get(carta, "🃏")
        badges.append(f"[bold bright_green]✔ {icone} {carta}[/bold bright_green]")

    faixa_cartas = "   ".join(badges)
    legenda = (
        "[bold bright_green]ℹ️ Álibis confirmados em sua posse:[/bold bright_green] "
        "[bold bright_white]Você tem 100% de certeza que estas cartas [/bold bright_white]"
        "[bold bright_red]NÃO[/bold bright_red][bold bright_white] são a solução do crime![/bold bright_white]"
    )

    console.print(Panel(
        Group(
            Align.center(Text.from_markup(faixa_cartas)),
            Align.center(Text.from_markup(f"\n{legenda}"))
        ),
        title="[bold bright_green]🃏 SEUS ÁLIBIS CONFIRMADOS (CARTAS EM SUA POSSE)[/bold bright_green]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(0, 1)
    ))

def distribuir_cartas(num_jogadores: int):
    """
    Embaralha e divide todas as 11 cartas restantes integralmente entre os detetives.
    Independente do número de jogadores (2 a 4), todas as cartas são entregues e nenhuma sobra.
    """
    cartas_disponiveis = list(personagens + armas + locais)
    random.shuffle(cartas_disponiveis)

    cartas_jogadores = {f"jogador{i + 1}": [] for i in range(num_jogadores)}
    for idx, carta in enumerate(cartas_disponiveis):
        jogador_chave = f"jogador{(idx % num_jogadores) + 1}"
        cartas_jogadores[jogador_chave].append(carta)

    return cartas_jogadores

def verificar_acusacao(acusacao: Dict[str, str]) -> bool:
    """Verifica se a acusação confere exatamente com a solução."""
    return acusacao == solucao

def pedir_pista(cartas_jogadores: Dict[str, List[str]], pistas_jogador: List[str]):
    """
    Busca uma carta que está com os detetives para servir de pista (máx. 3).
    """
    if len(pistas_jogador) < 3:
        cartas_jogadores_flat = [carta for cartas in cartas_jogadores.values() for carta in cartas]
        for pista in pistas_jogador:
            if pista in cartas_jogadores_flat:
                cartas_jogadores_flat.remove(pista)
        if cartas_jogadores_flat:
            return random.choice(cartas_jogadores_flat)
        else:
            return "Não há mais pistas disponíveis."
    else:
        return "Você já recebeu o número máximo de pistas."

def jogar():
    """
    Fluxo principal do jogo: seleção de menu por setas,
    filtragem de cartas na mão do jogador, vidas e cortina de privacidade.
    """
    animar_briefing_regras()

    console.clear()
    banner = """[bold bright_magenta]
    ╔═══════════════════════════════════════════════════════════════╗
    ║       🕵️‍♂️  A S S A S S I N A R A M   A   L Ó G I C A  🔍        ║
    ║        Mesa de Dedução Formal — Edição Interativa             ║
    ╚═══════════════════════════════════════════════════════════════╝[/bold bright_magenta]
    """
    console.print(Align.center(Text.from_markup(banner)))

    # Validação do número de detetives
    while True:
        try:
            num_jogadores = IntPrompt.ask("[bold bright_cyan]Digite o número de detetives (2 a 4)[/bold bright_cyan]")
            if 2 <= num_jogadores <= 4:
                break
            console.print("[bold bright_red]Número inválido! Selecione entre 2 e 4 jogadores.[/bold bright_red]")
        except Exception:
            console.print("[bold bright_red]Entrada inválida. Digite um número inteiro.[/bold bright_red]")

    # Nomes dos investigadores
    jogadores = {}
    for i in range(num_jogadores):
        nome = Prompt.ask(f"[bold bright_green]Nome do Detetive {i + 1}[/bold bright_green]").strip()
        if not nome:
            nome = f"Detetive {i + 1}"
        jogadores[f"jogador{i + 1}"] = nome

    # Inicialização de dados, pistas e VIDAS (3 por detetive)
    cartas_jogadores = distribuir_cartas(num_jogadores)
    pistas_jogadores = {jogador: [] for jogador in jogadores.keys()}
    cartas_descartadas = {jogador: set() for jogador in jogadores.keys()}
    crimes_detectados = {jogador: set() for jogador in jogadores.keys()}
    vidas_jogadores = {jogador: 3 for jogador in jogadores.keys()}

    animar_distribuicao_cartas(jogadores, cartas_jogadores)

    jogador_atual = 1

    # Loop de turnos
    while True:
        # Verifica se ainda existem jogadores vivos
        jogadores_vivos = [j for j, v in vidas_jogadores.items() if v > 0]
        if not jogadores_vivos:
            console.clear()
            console.print(Panel(
                Align.center(
                    "[bold bright_red]💀 TODOS OS DETETIVES FORAM ELIMINADOS! 💀[/bold bright_red]\n\n"
                    "[bright_white]Todas as vidas se esgotaram em acusações infundadas.\n"
                    "O crime contra a Lógica Formal permaneceu sem solução nos autos.[/bright_white]\n\n"
                    f"[bold bright_yellow]O CRIME REAL FOI:[/bold bright_yellow] [bold bright_magenta]{solucao['personagem']}[/bold bright_magenta] "
                    f"[bright_white]com[/bright_white] [bold bright_red]{solucao['arma']}[/bold bright_red] "
                    f"[bright_white]em[/bright_white] [bold bright_cyan]{solucao['local']}[/bold bright_cyan]."
                ),
                border_style="bright_red",
                box=box.DOUBLE,
                padding=(0, 2)
            ))
            return

        for idx_j in range(1, num_jogadores + 1):
            jogador = f"jogador{idx_j}"
            nome = jogadores[jogador]

            # Pula jogador eliminado (0 vidas)
            if vidas_jogadores[jogador] <= 0:
                continue

            # ============================================================
            # CORTINA DE PRIVACIDADE: O PAINEL SÓ APARECE PARA QUEM JOGA
            # ============================================================
            console.clear()
            coracoes_atual = "❤️ " * vidas_jogadores[jogador] + "🖤 " * (3 - vidas_jogadores[jogador])
            console.print(Panel(
                Align.center(
                    f"[bold bright_red]🔒 CORTINA DE PRIVACIDADE E SIGILO DOSSIÊ 🔒[/bold bright_red]\n\n"
                    f"[bright_white]ATENÇÃO: Demais detetives, [/bright_white]"
                    f"[bold bright_yellow]DESVIEM O OLHAR DO MONITOR AGORA![/bold bright_yellow]\n\n"
                    f"[bright_white]Turno exclusivo de:[/bright_white] [bold bright_cyan]{nome.upper()}[/bold bright_cyan]\n"
                    f"[bright_white]Vidas disponíveis:[/bright_white] [bold bright_red]{coracoes_atual.strip()} ({vidas_jogadores[jogador]}/3)[/bold bright_red]\n\n"
                    f"[bold bright_green]➤ Detetive {nome.upper()}, pressione [ ENTER ] quando estiver sozinho(a) diante da tela...[/bold bright_green]"
                ),
                border_style="bright_red",
                box=box.HEAVY,
                padding=(0, 2)
            ))
            Prompt.ask("")

            turno_concluido = False
            while not turno_concluido:
                # Renderiza a mesa dinâmica individual e confidencial
                exibir_mesa_dinamica(
                    nome_jogador=nome,
                    cartas_jogador=cartas_jogadores[jogador],
                    pistas_reveladas=pistas_jogadores[jogador],
                    cartas_descartadas=cartas_descartadas[jogador],
                    crimes_detectados=crimes_detectados[jogador],
                    vidas=vidas_jogadores[jogador]
                )

                # Exibe os álibis confirmados na mão
                exibir_mao_do_jogador(cartas_jogadores[jogador])

                console.print(f"\n[bold bright_cyan]❯❯ VEZ DO DETETIVE: {nome.upper()}[/bold bright_cyan]\n")

                # Seleção de ação com setas de navegação e highlight
                pistas_restantes = 3 - len(pistas_jogadores[jogador])
                acao = selecionar_acao_turno(pistas_restantes)

                # Investigação de cartas por setas e highlight
                if acao in {"p", "a", "l"}:
                    cat_info = {
                        "p": ("Suspeito", TODOS_PERSONAGENS, "👤", "bright_magenta"),
                        "a": ("Arma", TODAS_ARMAS, "🗡️", "bright_red"),
                        "l": ("Local", TODOS_LOCAIS, "🏛️", "bright_cyan")
                    }[acao]
                    cat_titulo, lista_itens, icone_sel, cor_sel = cat_info

                    # Não mostra cartas já confirmadas em mãos ou já elucidadas no dossiê
                    cartas_conhecidas = set(cartas_jogadores[jogador]) | cartas_descartadas[jogador] | crimes_detectados[jogador]
                    opcoes_disponiveis = [item for item in lista_itens if item not in cartas_conhecidas]

                    if not opcoes_disponiveis:
                        console.print(Panel(
                            Align.center(
                                f"[bold bright_yellow]ℹ️ TODAS AS EVIDÊNCIAS CONHECIDAS![/bold bright_yellow]\n\n"
                                f"[bright_white]Você já solucionou todos os [/bright_white][bold {cor_sel}]{cat_titulo}s[/bold {cor_sel}]!\n"
                                f"[bright_white]Não há mais cartas desconhecidas desta categoria.[/bright_white]"
                            ),
                            border_style="bright_yellow",
                            box=box.ROUNDED,
                            padding=(0, 1)
                        ))
                        Prompt.ask("\n[bold bright_cyan]Pressione ENTER para escolher outra ação...[/bold bright_cyan]")
                        continue

                    pergunta = selecionar_com_setas(cat_titulo, opcoes_disponiveis, icone_sel, cor_sel)

                    # Verifica sigilosamente se há álibi nos autos (se algum detetive tem a carta)
                    carta_tem_alibi = False
                    for j_cod, c_lista in cartas_jogadores.items():
                        if j_cod != jogador and pergunta in c_lista:
                            carta_tem_alibi = True
                            break

                    if carta_tem_alibi:
                        # Álibi anônimo comprovado: NÃO diz quem tem, apenas que está descartada
                        animar_virada_de_carta(pergunta, cat_titulo, status_final="descartada")
                        cartas_descartadas[jogador].add(pergunta)
                        console.print(Panel(
                            Align.center(
                                f"[bold bright_green]✔ ÁLIBI COMPROVADO NOS AUTOS![/bold bright_green]\n\n"
                                f"[bright_white]A perícia averiguou e confirmou um álibi formal para [/bright_white][bold {cor_sel}]'{pergunta}'[/bold {cor_sel}]!\n"
                                f"[bright_white]Esta evidência é inocente e foi marcada exclusivamente em seu dossiê como [/bright_white]\n"
                                f"[bold bright_red]INOCENTE DESCARTADA (✖)[/bold bright_red][bright_white]![/bright_white]"
                            ),
                            border_style="bright_green",
                            box=box.ROUNDED,
                            padding=(0, 1)
                        ))
                    else:
                        # Se não há álibi com nenhum detetive, está no envelope do crime
                        animar_virada_de_carta(pergunta, cat_titulo, status_final="crime")
                        crimes_detectados[jogador].add(pergunta)
                        console.print(Panel(
                            Align.center(
                                f"[bold bright_yellow]⚠️ NENHUM ÁLIBI LOCALIZADO! ⚠️[/bold bright_yellow]\n\n"
                                f"[bright_white]A perícia não encontrou nenhum álibi ou registro para [/bright_white][bold {cor_sel}]'{pergunta}'[/bold {cor_sel}]!\n"
                                f"[bright_white]Ela é uma evidência sem justificativa e foi isolada em seu dossiê como [/bright_white]\n"
                                f"[bold bright_yellow]FORTE SUSPEITA DO ENVELOPE (🎯)[/bold bright_yellow][bright_white]![/bright_white]"
                            ),
                            border_style="bright_yellow",
                            box=box.ROUNDED,
                            padding=(0, 1)
                        ))

                    turno_concluido = True

                # Acusação final por setas e highlight com penalidade de vida
                elif acao == "k":
                    console.print("\n[bold bright_red]⚠️ FORMALIZANDO ACUSAÇÃO NO TRIBUNAL ⚠️[/bold bright_red]")
                    console.print(f"[bold bright_yellow]Atenção: Um erro consumirá 1 das suas vidas ({vidas_jogadores[jogador]}/3)![/bold bright_yellow]\n")

                    opcoes_suspeitos = [p for p in TODOS_PERSONAGENS if p not in cartas_jogadores[jogador]]
                    opcoes_armas = [a for a in TODAS_ARMAS if a not in cartas_jogadores[jogador]]
                    opcoes_locais = [l for l in TODOS_LOCAIS if l not in cartas_jogadores[jogador]]

                    acusacao_personagem = selecionar_com_setas("Suspeito Acusado", opcoes_suspeitos, "👤", "bright_magenta")
                    acusacao_arma = selecionar_com_setas("Arma do Crime", opcoes_armas, "🗡️", "bright_red")
                    acusacao_local = selecionar_com_setas("Local dos Fatos", opcoes_locais, "🏛️", "bright_cyan")

                    acusacao_jogador = {
                        "personagem": acusacao_personagem,
                        "arma": acusacao_arma,
                        "local": acusacao_local
                    }

                    esta_correto = verificar_acusacao(acusacao_jogador)
                    animar_roleta_acusacao(acusacao_jogador, esta_correto)

                    if esta_correto:
                        animar_tela_vitoria(nome)
                        console.print(Panel(
                            Align.center(
                                f"[bold bright_yellow]O CRIME FOI SOLUCIONADO COM SUCESSO![/bold bright_yellow]\n\n"
                                f"👤 Culpado: [bold bright_magenta]{solucao['personagem']}[/bold bright_magenta]   "
                                f"🗡️ Arma: [bold bright_red]{solucao['arma']}[/bold bright_red]   "
                                f"🏛️ Local: [bold bright_cyan]{solucao['local']}[/bold bright_cyan]"
                            ),
                            border_style="bold bright_green",
                            box=box.DOUBLE,
                            padding=(0, 1)
                        ))
                        return
                    else:
                        vidas_jogadores[jogador] -= 1
                        animar_perda_de_vida(nome, vidas_jogadores[jogador])

                        if vidas_jogadores[jogador] <= 0:
                            animar_tela_derrota()
                            console.print(Panel(
                                Align.center(
                                    f"[bold bright_red]💀 DETETIVE {nome.upper()} FOI DEFINITIVAMENTE ELIMINADO! 💀[/bold bright_red]\n\n"
                                    f"[bright_white]Suas 3 vidas se esgotaram. Suas cartas continuam em jogo como álibis,\n"
                                    f"mas você não poderá mais realizar investigações ou acusações.[/bright_white]"
                                ),
                                border_style="bright_red",
                                box=box.HEAVY,
                                padding=(0, 1)
                            ))
                        turno_concluido = True

                # Pedido de pista com radar forense
                elif acao == "t":
                    animar_radar_pista(nome)
                    pista = pedir_pista(cartas_jogadores, pistas_jogadores[jogador])

                    if pista in ["Não há mais pistas disponíveis.", "Você já recebeu o número máximo de pistas."]:
                        console.print(Panel(f"[bold bright_yellow]{pista}[/bold bright_yellow]", border_style="bright_yellow", padding=(0, 1)))
                    else:
                        cat = "Suspeito" if pista in TODOS_PERSONAGENS else ("Arma" if pista in TODAS_ARMAS else "Local")
                        animar_virada_de_carta(pista, cat, status_final="pista")

                        console.print(Panel(
                            f"[bold bright_yellow]💡 PISTA REVELADA:[/bold bright_yellow] [bold bright_white]{nome}[/bold bright_white], "
                            f"[bright_white]a evidência descoberta nos arquivos é:[/bright_white] [bold bright_cyan]{pista}[/bold bright_cyan]!",
                            border_style="bright_yellow",
                            padding=(0, 1)
                        ))
                        pistas_jogadores[jogador].append(pista)

                    turno_concluido = True

            Prompt.ask("\n[bold bright_white]Pressione [ ENTER ] para ocultar o dossiê e passar a vez...[/bold bright_white]")

            # Oculta instantaneamente a tela do jogador antes de passar o controle
            console.clear()
            proximo_idx = (idx_j % num_jogadores) + 1
            proximo_jogador = jogadores[f"jogador{proximo_idx}"]

            console.print(Panel(
                Align.center(
                    f"[bold bright_yellow]🔒 PAINEL BLOQUEADO POR SEGURANÇA 🔒[/bold bright_yellow]\n\n"
                    f"[bright_white]Todas as evidências do Detetive [/bright_white][bold bright_cyan]{nome.upper()}[/bold bright_cyan] [bright_white]foram lacradas.[/bright_white]\n\n"
                    f"[bold bright_yellow]Chame o próximo investigador:[/bold bright_yellow] [bold bright_green]Detetive {proximo_jogador.upper()}[/bold bright_green]\n\n"
                    f"[bold bright_white]Pressione [ ENTER ] para preparar a estação de trabalho...[/bold bright_white]"
                ),
                border_style="bright_cyan",
                box=box.DOUBLE,
                padding=(0, 1)
            ))
            Prompt.ask("")

if __name__ == "__main__":
    jogar()