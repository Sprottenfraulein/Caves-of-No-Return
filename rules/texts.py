# Dictionary with all game text.
game_text = {
	'game_version': ('V1.3B',),
	'game_author': (
		'BY CEREAL KILLER,',
		'      2021'
	),
	'menu_controls': (
		'NEW GAME:SPACE,QUIT:ESCAPE,',
		' PREVIOUS,NEXT:A,D KEYS'
	),
	'inter_controls': (
		'CONTINUE:SPACE,QUIT:ESCAPE,',
		' PREVIOUS,NEXT:A,D KEYS'
	),
	'ending_controls_n': (
		'CONTINUE:SPACE',
	),
	'ending_controls_hs': (
		'CONTINUE:ENTER',
	),
	'ending_controls_q': (
		'QUIT:ESCAPE',
	),
	'newbie_message': (
		'BRIEFING FOR THE NEWCOMERS:',
		'          D KEY'
	),
	'dead_message': (
		'YOU HAVE DIED IN A DESPERATE ATTEMPT',
		'   TO FIND THE FLASK OF SPRINGS.',
		'            TRY AGAIN!'
	),
	'lost_message': (
		'    YOU WANDERED FURTHER AND FURTHER,',
		'   NEVER LOSING HOPE TO FIND THE FLASK',
		'  OF SPRINGS. MAY BE YOU ARE STILL ALIVE',
		'  AND TRYING, SOMEWHERE IN THE DEEPS OF',
		'THE UNDERWORLD. OR MAY BE YOU EVEN SUCCEED',
		'  IN SAVING YOUR VILLAGE SOMEHOW, WITHOUT',
		'      THE LEGENDARY MAGICAL DEVICE.',
		'  ANYWAY IT IS A STORY FOR ANOTHER TIME.',
		'                TRY AGAIN!'
	),
	'final_message': (
		'      GONE THROUGH THE HELL ITSELF,',
		'    YOU FINALLY ACCOMPLISH YOUR QUEST!',
		'YOU RETURN TO THE SURFACE HOLDING THE FLASK',
		'   OF SPRINGS IN YOUR HAND JUST IN TIME',
		'      TO WITNESS THE BEAUTIFUL DAWN.',
		'',
		' A LONG ROAD HOME AWAITS YOU,SO YOU NEED',
		'     TO REST FOR A WHILE.NO WORRIES!',
		'     SOON,YOUR VILLAGE WILL FLOURISH',
		'   AND PEOPLE WILL FOREVER REMEMBER YOU ',
		'        AS THEIR HERO AND SAVIOR.'
	),
	'menu_intro_h': ('EXPLORE THE DANGEROUS CAVES!',),
	'menu_gameover_h': ('GAME OVER',),
	'menu_intermission_h': ('INTERMISSION',),
	'menu_hiscores_h': ('THE BEST EXPLORERS OF THE CAVES',),
	'menu_final': ('CONGRATULATIONS!',),
	'menu_intro_p': (
		' YOU ARE AN ADVENTURER THAT LEFT HOME',
		' VILLAGE IN THE QUEST FOR THE MAGICAL',
		'FLASK OF SPRINGS.DESCEND INTO DARKNESS,',
		' FIND THE DEVICE AND SAVE YOUR TRIBE',
		'        FROM INEVITABLE DOOM!',
	),
	'interm_grounded': (
		'  VERMINS AND TRAPS MAKE ANXIETY BLOOM,',
		'  ENCOURAGING HASTY ILL-FATED DECISIONS.',
		'CAREFUL PROCEEDING WILL SAVE YOU FROM DOOM.',
		'     KEEP GROUNDED CLEVER AMBITIONS!',
		'',
		'      THERE IS NOTHING MORE TO TELL.',
		'       GO,IT IS ALL UP TO YOU NOW!',
	),
	'interm_meet': (
		'    IN THE CAVES DEVOID OF LIGHT,',
		'   INFESTED WITH HOSTILE CREATURES,',
		'THERE IS ALWAYS TINY CHANCE YOU MIGHT',
		'MEET SOMEONE WITH OUTSTANDING FEATURES!',
		'',
		'    THERE IS NOTHING MORE TO TELL.',
		'     GO,IT IS ALL UP TO YOU NOW!',
	),
	'interm_fiddle': (
		'THERE IS NO ANSWER RIGHT OR WRONG',
		'  FOR MANY COMPLICATED RIDDLES.',
		'BE NOT AFRAID OF GOBLINS TONGUE',
		'  AND PLAY THEM LIKE A FIDDLE.',
		'',
		'  THERE IS NOTHING MORE TO TELL.',
		'   GO,IT IS ALL UP TO YOU NOW!',
	),
	'menu_fullcontrols': (
		'  MOVEMENT:   W,A,S,D',
		'  ITEMS:      DIGITS 1 TO 9',
		'  SAY ALOUD:  RETURN',
		'  WAIT:       SPACEBAR',
		'  EXIT:       ESCAPE'
	),
	'stats_text': (
		'LIFE:',
		'POWER:',
		'MAGIC:',
		'GOLD COINS:'
	),
	'items_text': (
		'INVENTORY:',
	),
	'effects_text': (
		'EFFECTS:',
	),
	'cave_npgb': 'THERE IS NO POINT TO GO BACK.',
	'cave_echo': 'YOU HEAR AN ECHO:%s!',
	'cave_say': 'YOU SAY ALOUD:',
	'cave_wait': 'YOU STAY AWHILE AND LISTEN.',
	'cave_drop': 'YOU DROP %s.',
	'cave_ptn_red': 'YOU DRINK %s AND RESTORE %s HP.',
	'cave_ptn_yellow': 'YOU DRINK %s AND FEEL BETTER!',
	'cave_ptn_blue': 'YOU DRINK %s AND RESTORE %s MP.',
	'cave_use': 'YOU USE %s.',
	'cave_harm': 'TRAP WOUNDS YOU FOR %s HP!',
	'cave_poison': 'TRAP POISONS YOU!',
	'cave_immune': 'RUN! YOUR BLADE DOES NO HARM TO THE %s!',
	'cave_pc_attack': 'YOU HIT %s FOR %s HP.',
	'cave_mob_attack': 'THE %s WOUNDS YOU FOR %s HP.',
	'cave_blowaway': 'HEAVY STRIKE BLOWS YOU BACK!',
	'cave_smoke': 'SMOKING MAKES YOU COUGH.',
	'cave_nothing': 'NOTHING HAPPENS',
	'cave_loot': 'THE %s DIES AND DROPS %s.',
	'cave_noloot': 'THE %s DIES.',
	'cave_cured': 'YOU FEEL BETTER!',
	'cave_poisoned': 'YOU FEEL SICK!',
	'cave_rockpit': 'THE ROCK FALLS INTO THE PIT.',
	'cave_stoneblock': '%s BLOCKS THE WAY.',
	'cave_sus': 'THE %s BEHAVES SUSPICIOUSLY.',
	'cave_faints': 'THE EVIL PRESENCE FAINTS.',
	'cave_encounter': 'YOU SENSE A CREATURE LURKING NEARBY!',
	'cave_cast': 'YOU CAST %s SPELL.',
	'cave_lowmag': 'SPELL FAILS BECAUSE OF LOW MP.',
	'cave_flask': 'YOU FIND THE FLASK OF SPRINGS!',
	'cave_unreadable': 'THE WRITINGS ARE UNREADABLE.',
	'cave_hpup': 'YOUR VITALITY GROWS!',
	'cave_powup': 'YOUR MIGHT GROWS!',
	'cave_magup': 'YOUR MAGIC POTENCY GROWS!',
	'cave_murder': 'YOU ARE A MURDERER NOW.',
	'cave_maxed': 'YOU CAN NOT IMPROVE THE DISCIPLINE ANY FURTHER.'
}

dlg_common = {
	'no_gold': '-You can not afford it-',
	'murderer': 'Begone! You monster!',
	'bye': 'Farewell.'
}
dlg_human = {
	'name': 'Do our names even matter in the current circs!',
	'hello': 'Greetings, wanderer.',
	'lore': 'My knowledge of this place is quite limited.',
	'heal': 'For %s gold I can -prepare- some medicine.',
	'prepare': '-Your wounds are being healed-',
	'melody': 'The locals have some -bizarre- music taste!',
	'bizarre': 'Want me to -play- the tune on my device?',
	'play': 'Here you go...',
	'stop': 'I understand you.'
}
dlg_goblin = {
	'name': 'No rsssns sayin it onto yue.',
	'hello': 'Hie.',
	'lore': 'Sstay way frm our flk,ssnikie bsstrds them all.',
	'traps': 'Yss, lotss of trpss!Yu pai,them -dsschrge-.',
	'dsschrge': 'Yu -pai-!Me shhhal spik.',
	'pai': 'Nicce,nicce! -the Goblin vanishes in tunnels-'
}
