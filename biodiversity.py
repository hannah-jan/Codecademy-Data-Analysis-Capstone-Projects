from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency
import pandas as pd


species = pd.read_csv("species_info.csv")
observations = pd.read_csv("observations.csv")

#print(species.head())
print(observations.head())

# How many different species are in the species DataFrame?
print(species.scientific_name.nunique())


# What are the different values of category in species?
print(species.category.unique())


# What are the different values of conservation_status?
print(species.conservation_status.unique())


# How many animals are in each conservation_status?
print(species.groupby('conservation_status')\
             .scientific_name.nunique()\
             .reset_index())

    
# Fill empty columns and create protected species df

species = species.fillna(value={'conservation_status':'No Intervention'})

protection_counts = species.groupby('conservation_status')\
    .scientific_name.nunique().reset_index()\
    .sort_values(by='scientific_name')

protection_counts.rename(columns = {'scientific_name': 'Number of species', 'conservation_status': 'Conservation Status'}, inplace=True)
print(protection_counts)
    

# Plot the protected species data
figsize=(10, 4)
ax = plt.subplot()
plt.bar(range(len(protection_counts)), protection_counts['Number of species'])
ax.set_xticks(range(len(protection_counts)))
ax.set_xticklabels(protection_counts['Conservation Status'], rotation=30)
plt.ylabel('Number of Species')
plt.title('Conservation Status by Species')
plt.show()


# Are certain types of species more likely to be endangered?

species['is_protected'] = species.conservation_status.apply(lambda x:  x != 'No Intervention')
print(species[['conservation_status', 'is_protected']])

category_counts = species.groupby(['category','is_protected']).scientific_name.nunique().reset_index()
print(category_counts.head())

category_pivot = category_counts.pivot(columns= 'is_protected',\
                                       index = 'category', \
                                       values = 'scientific_name')\
                                .reset_index()
category_pivot.columns = ['category', 'not_protected', 'protected']
category_pivot['percent protected'] = 100*category_pivot['protected']/(category_pivot['protected']+ category_pivot['not_protected'])

print(category_pivot)

# Chi-square test for hypothesis: Mammals are more likely to be protected than birds

contingency = [[75, 413],  # bird
               [30, 146]] # mammal
print(chi2_contingency(contingency)) #not significant

# Chi-square test for hypothesis: Mammals are more likely to be protected than reptiles

contingency = [[5, 73],  # reptile
               [30, 146]] # mammal
print(chi2_contingency(contingency)) # significant!


# Finding sheep in observations data
species['is_sheep'] = species.common_names.apply(lambda x: 'Sheep' in x)
sheep_species = species[(species.is_sheep) &(species.category == 'Mammal')]


sheep_observations = observations.merge(sheep_species)
print(sheep_observations)
obs_by_park = sheep_observations.groupby('park_name').observations.sum().reset_index()
print(obs_by_park)

plt.figure(figsize=(16, 4))
ax = plt.subplot()
plt.bar(range(len(obs_by_park)),
        obs_by_park.observations.values)
ax.set_xticks(range(len(obs_by_park)))
ax.set_xticklabels(obs_by_park.park_name.values)
plt.ylabel('Number of Observations')
plt.title('Observations of Sheep per Week')
plt.show()

# Sample Size Determination: How many weeks to observe whether program successfully
# can reduce disease from 15% to 10%  in Bryce and Yellowstone National Park?

minimum_detectable_effect = abs(100*(10 - 15)/15)
baseline = 15
sample_size = 870 #from sample size calculator

number_of_weeks_bryce = 870 / 250
number_of_weeks_yellow = 870 / 507


