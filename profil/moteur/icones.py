"""Icônes du kit badolo : géométriques, trait épais et arrondi, et toujours un point orange plein."""

I = "{ink}"


def dot(cx, cy, r=3.6):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{{ac}}" stroke="none"/>'


ICONS = {
    "mail": ("M'écrire", f'<rect x="6" y="11" width="36" height="26" rx="5" stroke="{I}"/><path d="M9 15 L21 24.5 M39 15 L27 24.5" stroke="{I}"/>' + dot(24, 26.5)),
    "profil": ("Profil", f'<rect x="6" y="10" width="36" height="28" rx="5" stroke="{I}"/><circle cx="18" cy="21" r="4" stroke="{I}"/>'
                         f'<path d="M12 32 C13 28, 23 28, 24 32 M29 20 H36 M29 27 H34" stroke="{I}"/>' + dot(41, 9, 3.4)),
    "globe": ("Site", f'<circle cx="24" cy="25" r="16" stroke="{I}"/><ellipse cx="24" cy="25" rx="6.5" ry="16" stroke="{I}"/><path d="M8 25 H40" stroke="{I}"/>' + dot(38, 10, 3.4)),
    "code": ("Code", f'<path d="M16 13 L6 24 L16 35 M32 13 L42 24 L32 35" stroke="{I}"/>' + dot(24, 24, 4.2)),
    "bulle": ("IA", f'<path d="M11 9 H37 Q42 9 42 14 V28 Q42 33 37 33 H21 L13 40 V33 H11 Q6 33 6 28 V14 Q6 9 11 9 Z" stroke="{I}"/>'
                    f'<circle cx="16" cy="21" r="1.4" fill="{I}"/><circle cx="32" cy="21" r="1.4" fill="{I}"/>' + dot(24, 21, 2.8)),
    "data": ("Data", f'<ellipse cx="24" cy="11" rx="15" ry="5" stroke="{I}"/><path d="M9 11 V37 C9 40, 16 42, 24 42 C32 42, 39 40, 39 37 V11" stroke="{I}"/>'
                     f'<path d="M9 24 C9 27, 16 29, 24 29 C32 29, 39 27, 39 24" stroke="{I}"/>' + dot(24, 11, 2.8)),
    "courbe": ("Maths", f'<path d="M8 6 V40 H42" stroke="{I}"/><path d="M12 12 C18 40, 30 40, 38 14" stroke="{I}"/>' + dot(24.3, 33.2, 3.8)),
    "oeil": ("Vision", f'<path d="M4 24 C10 13, 38 13, 44 24 C38 35, 10 35, 4 24 Z" stroke="{I}"/>' + dot(24, 24, 5.4)),
    "note": ("Musique", f'<path d="M18 36 V10 L38 6 V32 M18 15 L38 11" stroke="{I}"/><ellipse cx="13.5" cy="36" rx="5" ry="4" stroke="{I}"/>'
                        f'<ellipse cx="33.5" cy="32" rx="5.4" ry="4.4" fill="{{ac}}" stroke="none"/>'),
    "ballon": ("Foot", f'<circle cx="24" cy="24" r="17" stroke="{I}"/><path d="M24 7 V15 M40.2 18.7 L32.5 21.2 M34 37.8 L29.3 31.3 M14 37.8 L18.7 31.3 M7.8 18.7 L15.5 21.2" stroke="{I}"/>' + dot(24, 24.5, 5.2)),
    "loupe": ("Anomalies", f'<circle cx="20" cy="20" r="12.5" stroke="{I}"/><path d="M29.5 29.5 L41 41" stroke="{I}"/>' + dot(23.5, 16.5, 3.2)),
    "route": ("Itinéraire", f'<circle cx="10" cy="37" r="3.6" stroke="{I}"/><path d="M13 33 C15 22, 24 30, 26 22 C28 15, 31 14, 34 13.5" stroke="{I}" stroke-dasharray="0.5 6"/>' + dot(38, 11, 4.2)),
    "cube": ("3D", f'<path d="M24 6 L40 15 V33 L24 42 L8 33 V15 Z M8 15 L24 24 L40 15 M24 24 V42" stroke="{I}"/>' + dot(24, 24, 3.4)),
    "coeur": ("Avec le cœur", f'<path d="M24 40 C10 31, 5 23, 8 16 C11 9, 20 9, 24 16 C28 9, 37 9, 40 16 C43 23, 38 31, 24 40 Z" stroke="{I}"/>' + dot(39.5, 8.5, 3.4)),
    "eclair": ("Vivacité", f'<path d="M26 4 L10 27 H21 L18 44 L36 19 H25 L26 4 Z" stroke="{I}"/>' + dot(40, 8, 3.4)),
    "ampoule": ("Astuce", f'<path d="M18 31 C12 27, 10 21, 12 16 C15 8, 33 8, 36 16 C38 21, 36 27, 30 31 V35 H18 Z M19 40 H29" stroke="{I}"/>' + dot(24, 20, 3.8)),
    "carre": ("Tout carré", f'<rect x="8" y="10" width="30" height="30" rx="3" stroke="{I}"/><path d="M15 25 L21 31 L31 19" stroke="{I}"/>' + dot(40, 8, 3.4)),
    "agenda": ("Plans", f'<rect x="7" y="10" width="34" height="31" rx="5" stroke="{I}"/><path d="M7 18 H41 M16 6 V13 M32 6 V13" stroke="{I}"/>' + dot(31, 30, 3.8)),
    "graphe": ("Graphes", f'<path d="M12.1 32 L21.9 14 M26.1 14 L35.9 32 M14.5 36 H33.5 M20.2 29.4 L13.8 33.6 M24 22.5 V14.5 M27.8 29.4 L34.2 33.6" stroke="{I}"/>'
                          f'<circle cx="10" cy="36" r="4" stroke="{I}"/><circle cx="24" cy="10" r="4" stroke="{I}"/><circle cx="38" cy="36" r="4" stroke="{I}"/>' + dot(24, 27, 4)),
}
