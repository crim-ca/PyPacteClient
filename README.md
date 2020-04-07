# PyPacteClient

(For English, see below.)

Client Python pour un accès simplifié aux données et fonctionnalités de la [plateforme PACTE](http://pacte.crim.ca).

## Utilisation

Définir l'adresse du serveur et vos accès à l'instance de PACTE utilisé :

```
config = QuickConfig.configForUser( "https://patx-pacte.crim.ca", "<nom utilisateur>", "<mot de passe>")
```

Vous pouvez alors instancier la classe nécessaire pour avoir accès aux fonctions (ici avec la classe `Corpus`) :

```
corpus = CorpusManager(config)
id = corpus.createCorpus("Nouveau corpus", ["fr_fr", "en_en"])
```

## Contributeurs et remerciements

Ce client été produit par l’équipe [Parole et Texte](https://www.crim.ca/fr/equipes/parole-et-texte) du CRIM dans le cadre du projet [PACTE](http://pacte.crim.ca). Le projet a bénéficié du soutien financier de CANARIE et du ministère de l’Économie, de la Science et de l’Innovation (MESI) du gouvernement du Québec.

## Références
Si vous utilisez la plateforme PACTE pour vos recherches, prière d'utiliser la référence suivante :

[1] Ménard, P. A. et Barrière, C. "PACTE: a collaborative platform for textual annotation" dans Proceedings of the 12th International Conference on Computational Semantics (IWCS 2017). Montpellier, France, du 19 au 22 septembre 2017.

---

# PyPacteClient

Python client for an easy access to data and functionalities of [PACTE platform](http://pacte.crim.ca).

## Usage

Define the server address and your credentials for the PACTE's instance used:

```
config = QuickConfig.configForUser( "https://patx-pacte.crim.ca", "<nom utilisateur>", "<mot de passe>")
```

You can then use the required class to access related functions (here with the `Corpus` class) :

```
corpus = CorpusManager(config)
id = corpus.createCorpus("New corpus", ["fr_fr", "en_en"]);
```

## Credits and acknowledgements

This client has been produced by the [Speech and Text](https://www.crim.ca/en/teams/speech-and-text) team at CRIM as part of the [Pacte](http://pacte.crim.ca) project. The project was supported by CANARIE and the *ministère de l’Économie, de la Science et de l’Innovation* (MESI) of the Government of Québec.

## References
If you use the PACTE platform for your research, kindly use the following reference:

[1] Ménard, P. A. et Barrière, C. "PACTE: a collaborative platform for textual annotation" in Proceedings of the 12th International Conference on Computational Semantics (IWCS 2017). Montpellier, France, 19 to 22 September 2017
