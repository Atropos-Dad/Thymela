from webscraping.post_process_pride import pride_get_all_studies
from webscraping.post_process_mwb import mbw_get_all_studies
from tqdm import tqdm
from dbwrap.db_add_study import add_to_Pride_studies
from dbwrap.db_add_study import add_to_MBW_studies

# {
#     "accession": "PXD054577",
#     "title": "Intragenic DNA inversions expand bacterial coding capacity",
#     "projectDescription": "Bacteria can generate heterogeneity through phase variation, including enzyme-mediated inversion of specific intergenic regions of genomic DNA. We developed a computation tool that identifies invertible elements using long-read datasets, PhaVa. We identified over 300 \u2018intragenic invertons,\u2019 a new class of invertible elements entirely within genes, in both bacteria and archaea. In the gut commensal Bacteroides thetaiotaomicron, we experimentally characterized an intragenic inverton in the thiamine biosynthesis protein thiC. We used mass spectrometry in data-independent acquisition mode to identify and quantify B. theta proteins, including thiC inverton expression at the protein level.",
#     "sampleProcessingProtocol": "Bacteria were cultured, pelleted, and lysed in 5% SDS, 50 mM triethylammonium bicarbonate (TEAB), pH 8.5., and 1x HALT Protease and Phosphatase Inhibitor (Thermo Fisher Scientific). Samples were sonicated and cell debris was removed upon pelleting. Ten micrograms of protein per sample were reduced and alkylated with the incorporation of tris(2-carboxyethyl)phosphine (TCEP) and 2-chloroacetamide at final concentrations of 25 mM and 50 mM, respectively, followed by incubation at 70 degrees Celsius for 20 min. Aqueous phosphoric acid was added to samples at a final concentration of 2.5% and loaded onto S-Trap micro spin columns (Protifi) with binding buffer (100 mM TEAB, pH 7.55, and 90% methanol). S-Trap columns were used for desalting, digestion, and peptide extraction, following the manufacturer\u2019s protocol. Trypsin digestion was performed at a 1:25 enzyme:protein ratio (w/w) with incubation at 37 degrees Celsius overnight. Peptides were eluted, dried down in a SpeedVac, and resuspended in 0.1% formic acid, 4% acetonitrile, and 0.015% n-dodecyl \u03b2-D-maltoside at a final concentration of 0.15 \u00b5g/\u00b5L using UHPLC-MS water. A total of 0.15 \u00b5g (1 \u00b5L) was loaded on column for LC-MS/MS analysis. Peptides were analyzed by LC-MS/MS using a nanoElute 2 coupled to a timsTOF Ultra mass spectrometer (Bruker Daltonics). Peptides were separated using a one column method with a PepSep ULTRA C18 HPLC column (25 cm x 75 \u00b5m x 1.5 \u00b5m; Bruker) heated at 50 degrees Celsius, and a 10 \u00b5m emitter (Bruker) attached to a CaptiveSpray Ultra source. A linear gradient was run consisting of 3 to 34% buffer B over 30 min at a flow rate of 200 nL/min. The mobile phases were 0.1% formic acid in UHPLC-MS water (buffer A) and 0.1% formic acid/99.9% acetonitrile (buffer B). First, to optimize the data-independent acquisition (DIA) parallel accumulation serial fragmentation (PASEF) method, a data-dependent acquisition (DDA)-PASEF method was used on a testmix solution consisting of each sample at an equivalent ratio. For analysis in dia-PASEF mode, the MS scan range was set to 100 to 1700 m/z with positive ion polarity. TIMS settings included an ion mobility 1/K0 range from 0.65 to 1.46 V\u00b7s/cm2, ramp time of 50 ms, and 100% duty cycle. The py_diAID tool was applied to optimize the dia-PASEF method using a spectral library generated from the testmix sample. Sixteen dia-PASEF scans separated into three ion mobility windows per scan.",
#     "dataProcessingProtocol": "DIA data was analyzed in DIA-NN using an in silico spectral library generated with a custom B. theta FASTA. A Uniprot Reference proteome that included B. theta VPI-5482 (FASTA downloaded February 2024) was customized by appending the three predicted ThiC intragenic inverted ORFs. Precursor ion generation included prediction of deep learning-based spectra, retention times, and ion mobilities, in silico digestion with trypsin, a maximum of one missed cleavage, N-terminal methionine excision, fixed cysteine carbamidomethylation, precursor charge states of 1 to 4, and a fragment ion m/z range of 200 to 1800. From the DIA runs, a spectral library was generated and the resulting DIA identifications at the peptide and protein levels were normalized by MS1 intensity. Identified ThiC peptides were validated for quantitative comparisons based on reliable detection in at least one sample, as assessed in Skyline, and MS/MS spectra and extracted ion chromatograms from resulting peptides were visualized.",
#     "keywords": [
#       "Thih",
#       "Bacteroides thetaiotaomicron",
#       "Inverton",
#       "Thic",
#       "Dia",
#       "Intragenic dna inversion"
#     ],
#     "submissionDate": "2024-08-05",
#     "publicationDate": "2024-08-06",
#     "license": "Creative Commons Public Domain (CC0)",
#     "updatedDate": "2024-08-05",
#     "submitters": [
#       "Krystal Lum"
#     ],
#     "labPIs": [
#       "Ileana M. Cristea"
#     ],
#     "affiliations": [
#       "Princeton University"
#     ],
#     "instruments": [
#       "Timstof ultra"
#     ],
#     "organisms": [
#       "Bacteroides thetaiotaomicron (strain atcc 29148 / dsm 2079 / nctc 10582 / e50 / vpi-5482)"
#     ],
#     "organismParts": "unknown",
#     "references": [],
#     "queryScore": 1.0,
#     "diseases": "unknown",
#     "projectTags": "unknown"
#   },
def populate_pride():
    studies = pride_get_all_studies()
    for study in tqdm(studies, desc="Adding studies to db", unit="study"):
        # extract values from json study into list to add to db
        # needs to be in the order: "accession", "title", "projectDescription", "sampleProcessingProtocol", "dataProcessingProtocol", "keywords", "organisms", "organismParts", "diseases", "projectTags", "instruments"
        values = [
            study["accession"],
            study["title"],
            study["projectDescription"],
            study["sampleProcessingProtocol"],
            study["dataProcessingProtocol"],
            study["keywords"],
            study["organisms"],
            study["organismParts"],
            study["diseases"],
            study["projectTags"],
            study["instruments"],
        ]


        try:
            add_to_Pride_studies(values)
        except Exception as e:
            # add to tqdm progress bar
            print(f"Error adding {study['accession']} to db")
            print(e)
            input("Press enter to continue")

            
def populate_mbw():
    studies = mbw_get_all_studies()
    for study in tqdm(studies, desc="Adding studies to db", unit="study"):
        try:
            add_to_MBW_studies(study)
        except Exception as e:
            # add to tqdm progress bar
            print(f"Error adding {study['studyId']} to db")
            print(e)
            input("Press enter to continue")