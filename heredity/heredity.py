import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    # For each person in people, record number of genes and whether or not they have the trait depending on input
    gene_trait_dict = {}

    # Get key, representing each person, in dictionary people
    for person in people:

        # person has one copy of the gene
        if person in one_gene:
            gene = 1
            if person in have_trait:
                trait = True
            else:
                trait = False

        # person has two copies of the gene
        elif person in two_genes:
            gene = 2
            if person in have_trait:
                trait = True
            else:
                trait = False
        # person has 0 copies of the gene
        else:
            gene = 0
            if person in have_trait:
                trait = True
            else:
                trait = False

        gene_trait_dict[person] = [gene, trait]

# Initiate list of factors to be multiplied together
    factors = []

    # Calculate joint probability for each person in people
    for person in gene_trait_dict:

        # Number of copies of given person and whether s/he has the trait
        gene = gene_trait_dict[person][0]
        trait = gene_trait_dict[person][1]

        # prob trait given the above "gene"
        prob_trait = PROBS["trait"][gene][trait]

        # Check if person's parents is known
        # None of our csv files give the single parent case, so we don't consider it
        mother = people[person]["mother"]
        father = people[person]["father"]

        if mother != None and father != None:

            # Number of copies of mother and father
            gene_mother = gene_trait_dict[mother][0]
            gene_father = gene_trait_dict[father][0]

            if gene == 0:

                # probability of receiving no copies from mother
                if gene_mother == 0:
                    prob_mother = 0.99
                elif gene_mother == 1:
                    prob_mother = 0.5
                else:
                    prob_mother = 0.01

                # probability of receiving no copies from father
                if gene_father == 0:
                    prob_father = 0.99
                elif gene_father == 1:
                    prob_father = 0.5
                else:
                    prob_father = 0.01

                # probability of receiving no copies from either (multiply the above)
                prob_gene = prob_mother * prob_father

            elif gene == 1:

                # person received {1 from mother, 0 from father}
                if gene_mother == 0:
                    prob_mother = 0.01
                elif gene_mother == 1:
                    prob_mother = 0.5
                else:
                    prob_mother = 0.99

                if gene_father == 0:
                    prob_father = 0.99
                elif gene_father == 1:
                    prob_father = 0.5
                else:
                    prob_father = 0.01

                prob_scen1 = prob_mother * prob_father

                # person received  {1 from father, 0 from mother}
                if gene_father == 0:
                    prob_father = 0.01
                elif gene_father == 1:
                    prob_father = 0.5
                else:
                    prob_father = 0.99

                if gene_mother == 0:
                    prob_mother == 0.99
                elif gene_mother == 1:
                    prob_mother = 0.5
                else:
                    prob_mother = 0.01

                prob_scen2 = prob_mother * prob_father

                # probability of receiving 1 copy via either scenario
                prob_gene = prob_scen1 + prob_scen2

            else:

                # person received 1 copy from mother
                if gene_mother == 0:
                    prob_mother = 0.01
                elif gene_mother == 1:
                    prob_mother = 0.5
                else:
                    prob_mother = 0.99

                # person received 1 copy from father
                if gene_father == 0:
                    prob_father = 0.01
                elif gene_father == 1:
                    prob_father = 0.5
                else:
                    prob_father = 0.99

                # probability of receiving 1 copy from each
                prob_gene = prob_mother * prob_father

        else:
            # We take probability of person having given gene from the distribution for the general population
            prob_gene = PROBS["gene"][gene]

        # probability that person has given copies of gene and given trait
        prob = prob_gene * prob_trait
        factors.append(prob)

    # Multiply to get joint probability
    product = 1
    for i in range(len(factors)):
        product = product * factors[i]

    return product


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        # Update number of genes
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        # Update trait value
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
        # Iterate over each person in the probabilities dictionary
    for person in probabilities:

        # Iterate over 0, 1, and 2 in the "genes" dictionary and add them up
        sum = 0
        for gene in probabilities[person]["gene"]:
            sum += probabilities[person]["gene"][gene]

        # Iterate over 0, 1, and 2 in the "genes" dictionary and divide each value
        # by the above sum
        for gene in probabilities[person]["gene"]:
            probabilities[person]["gene"][gene] = probabilities[person]["gene"][gene] / sum

        # Repeat the normalization for the "trait" dictionary
        sum = 0
        for trait in probabilities[person]["trait"]:
            sum += probabilities[person]["trait"][trait]
        for trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][trait] = probabilities[person]["trait"][trait] / sum


if __name__ == "__main__":
    main()
