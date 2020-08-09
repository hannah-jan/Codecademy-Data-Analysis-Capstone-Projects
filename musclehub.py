from codecademySQL import sql_query
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency


# Examine visits here
print(sql_query('''
SELECT *
FROM visits
LIMIT 5 '''))

# Examine fitness_tests here
print(sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5 '''))

# Examine applications here
print(sql_query('''
SELECT *
FROM applications
LIMIT 5 '''))

# Examine purchases here
print(sql_query('''
SELECT *
FROM purchases
LIMIT 5 '''))

# Create a df with relevant data

df = sql_query('''
SELECT visits.first_name,
    visits.last_name,
    visits.gender, 
    visits.email, 
    visits.visit_date, 
    fitness_tests.fitness_test_date,
    applications.application_date, 
    purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests
    ON visits.email = fitness_tests.email
    AND visits.first_name = fitness_tests.first_name
    AND visits.last_name = fitness_tests.last_name
LEFT JOIN applications
    ON visits.email = applications.email
    AND visits.first_name = applications.first_name
    AND visits.last_name = applications.last_name
LEFT JOIN purchases
    ON visits.email = purchases.email
    AND visits.first_name = purchases.first_name
    AND visits.last_name = purchases.last_name
WHERE visits.visit_date >= '7-1-17'
''')

print(len(df))

# Investigate the A/B groups

df['ab_test_groups'] = df.fitness_test_date.apply(lambda x: "A" if x is not None else "B")
ab_counts = df.groupby('ab_test_groups').count()

print(ab_counts)

plt.pie(ab_counts.first_name.values, autopct='%0.2f%%')
plt.axis('equal')
plt.show()
plt.savefig('ab_test_pie_chart.png')


# Who picks up an application?

df['is_application'] = df.application_date.apply(lambda x: 'Application' if x is not None else 'No Application')

app_counts = df.groupby(['ab_test_groups', 'is_application'])\
                .first_name.count()\
                .reset_index()
                
print(app_counts)

app_pivot = app_counts.pivot(columns = 'is_application',
                             index = 'ab_test_groups',
                             values = 'first_name').reset_index()

app_pivot['Total'] = app_pivot['Application'] + app_pivot['No Application']
app_pivot['Percent with Application'] = 100* app_pivot['Application']/app_pivot['Total']

print(app_pivot)

# Is the difference in who picks up an application significant? chi-square test

contingency = [[250, 2254], #A applications
               [325, 2175]] #B applications

pval = chi2_contingency(contingency)[1]

print(pval) #0.00096< 0.05 indicates difference in who picks up applications

# Who purchases a membership having picked up an application?

df['is_member'] = df.purchase_date.apply(lambda x: 'Member' if x is not None else 'Not Member')

just_apps = df[df.is_application == 'Application']



member_counts = just_apps.groupby(['ab_test_groups', 'is_member'])\
                .first_name.count()\
                .reset_index()
                
member_pivot = member_counts.pivot(columns = 'is_member',
                             index = 'ab_test_groups',
                             values = 'first_name').reset_index()

member_pivot['Total'] = member_pivot['Member'] + member_pivot['Not Member']
member_pivot['Percent Purchase'] = 100* member_pivot['Member']/member_pivot['Total']

print(member_pivot)

# Is the difference in who buys a membership significant? chi-square test

contingency_member = [[200, 50], #A purchases
               [250, 75]] #B purchases

pval_member = chi2_contingency(contingency_member)[1]

print(pval_member) #0.432 > 0.05 indicates not significant so can't show a difference


# Who purchases a membership having picked out of all visits?

final_member_counts = df.groupby(['ab_test_groups', 'is_member'])\
                                .first_name.count()\
                                .reset_index()
                
final_member_pivot = final_member_counts.pivot(columns = 'is_member',
                             index = 'ab_test_groups',
                             values = 'first_name').reset_index()

final_member_pivot['Total'] = final_member_pivot['Member'] + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = 100* final_member_pivot['Member']/final_member_pivot['Total']

print(final_member_pivot)

# Is the difference in who buys a membership significant? chi-square test

contingency_member_final = [[200, 2304], #A purchases
                            [250, 2250]] #B purchases

pval_member_final = chi2_contingency(contingency_member_final)[1]

print(pval_member_final) #0.0147 < 0.05 indicates that overall there is a difference between groups


# Summarise the acquisition funnel chart

# Percent of Visitors who Apply
ax = plt.subplot()
plt.bar(range(len(app_pivot)),
       app_pivot['Percent with Application'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
plt.title('Percentage of visitors who apply')
plt.show()
plt.savefig('percent_visitors_apply.png')

# Percent of Applicants who Purchase
ax = plt.subplot()
plt.bar(range(len(member_pivot)),
       member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'])
plt.title('Percentage of applicants who purchase a membership')
plt.show()
plt.savefig('percent_apply_purchase.png')


# Percent of Visitors who Purchase
ax = plt.subplot()
plt.bar(range(len(final_member_pivot)),
       final_member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 5, 10, 15, 20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
plt.title('Percentage of visitors who purchase a membership')
plt.show()
plt.savefig('percent_visitors_purchase.png')
