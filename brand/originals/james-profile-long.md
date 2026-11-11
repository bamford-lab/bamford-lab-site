---
name: James McCabe
role: PhD Researcher
order: 7
initials: JM
photo: "/assets/people/james.jpg"
projectLabel: Project
projectTitle: "EVOLVE-AI: Evolutionary-Informed Deep Learning for Deciphering and Modifying Cell-Cell Communication During Infection, Inflammation, and Cancer."
funders: "Funded by the BBSRC, through the NI Landscape partnership in AI for Bioscience (NILAB). Supervised by Connor Bamford, with Barry Devereux and Kyle Matchett."
outside: "I love playing golf, cricket and tennis, and I am a keen mountaineer."
links:
  - label: "QUB research profile"
    url: "https://www.qub.ac.uk/schools/SchoolofBiologicalSciences/Research/PostgraduateResearch/PGRStudents/JamesMcCabe-1.html"
  - label: "GitHub"
    url: "https://github.com/jsmccabe1"
sections:
  - heading: "My PhD"
    body: |
      Cytokines are the proteins cells use to talk to one another. They coordinate almost everything the immune system does, and when that signalling breaks down the consequences are significant: immunodeficiency, autoimmunity, chronic inflammation and cancer all trace back to cytokine signalling gone wrong. These systems are also hugely relevant for infectious disease, as viruses encode counterfeit cytokines and decoy receptors built to intercept the conversation and shut the host's defences down.

      EVOLVE-AI builds a residue-level map of these systems: not just which proteins matter, but which individual positions carry the function. The foundation is a comparative atlas of immune signalling proteins traced across thousands of vertebrate genomes, where every position is annotated with rich evolutionary information, from selection and ancestral history to coevolution between binding partners.

      AI protein language models are, in effect, evolutionary models: they learn what variation is possible from sequence alone. So this results in many evolutionary signals set against each other, some absorbed as a learned prior and some requiring explicit integration. My work asks where the learned signal goes blind, and whether that blindness is predictable rather than random. The applications run through infection, inflammation and cancer alike, because the same residues tend to matter in all three.
  - heading: "Beyond the PhD"
    body: |
      Away from the lab's research programme I enjoy writing open-source scientific software aimed at making large, messy biological datasets say something specific. SCEPTR (Statistical Characterisation of Expression Profiles in Transcriptomes) is one such tool, developed from my time working at the Institute of Microbiology of the Czech Academy of Sciences. It answers a simple question about a transcriptome: what is it doing, and where is it spending its resources? Rather than needing replicates, a control condition or an arbitrary cutoff, it traces a continuous enrichment profile for every functional category across the whole expression gradient, from a single sample against its own background, with no reference genome required. It is made for cases such as a tumour biopsy, a clinical parasite isolate, a drug-resistant pathogen, a virus-infected cell line. This work lives on [my GitHub](https://github.com/jsmccabe1).
figures:
  - src: "/assets/james-dawkins.jpg"
    caption: "Meeting evolutionary biologist Richard Dawkins, Belfast."
draft: false
---
Hi, I'm James, a second-year PhD student in the Bamford antiviral immunity lab, working where evolutionary biology, structural biology and artificial intelligence meet.

AI protein models already learn something about evolution, but they learn it from sequence databases skewed towards a handful of well-studied organisms. So what are they missing, and where? I combine those learned representations with the explicit, deep-time record of natural selection across thousands of vertebrate genomes to work out which residues in our immune signalling proteins carry function, and to map where the AI's view of them goes blind. The aim is to find the positions that drive disease, the sites viruses exploit, and the ones worth engineering into new therapeutics.
