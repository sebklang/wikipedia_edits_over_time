import requests
import collections
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates

params = {
    'action': 'query',
    'format': 'json',
    'prop':   'revisions',
    'rvlimit': 500,
    'rvstart':'2022-01-26T23:59:59Z',
    'rvend':  '2016-01-01T00:00:00Z',
    'rvprop': 'timestamp|user',
    'rvexcludeuser': 'Cyberbot_I', # Can only exclude one user. This bot posted 500 edits in 1 day
    'titles': 'Russo-Ukrainian War'
}
banned_users = ['Cyberbot_I', 'Aleksandr Grigoryev', 'RenatUK', '178.35.34.32']

timestamp_datetimes = []

while True:
    response = requests.get('https://en.wikipedia.org/w/api.php', params=params).json()
    timestamps = [rev['timestamp'] for rev in filter(lambda e: e['user'] not in banned_users, response['query']['pages']['42085878']['revisions'])]
    timestamp_datetimes.extend(map(lambda s: datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ'), timestamps))
    if 'continue' not in response:
        print('Reached final targeted revision')
        break
    else:
        if 'rvstart' in params:
            del params['rvstart']
        params['rvstartid'] = response['continue']['rvcontinue'].split('|')[1]

date_counts = collections.Counter(map(lambda stamp: stamp.date(), timestamp_datetimes))

dates = list(date_counts.keys())
values = list(date_counts.values())

print("no. of days =", dates[1] - dates[-1] + datetime.timedelta(days=1))

days_rolling_avg = 15
rolling_avg = {}
diff = datetime.timedelta(days=days_rolling_avg//2)
base_day = dates[0] - diff
while base_day >= dates[-1] + diff:
    date_range = [base_day + diff - datetime.timedelta(days=x) for x in range(days_rolling_avg)]
    date_values = list(map(lambda date: date_counts[date], date_range))
    rolling_avg[base_day] = sum(date_values)/len(date_values)
    base_day -= datetime.timedelta(days=1)

fig = plt.figure(figsize=(10.00, 6.50))
plt.style.use('fivethirtyeight')

ax1 = fig.add_subplot(111)
ax1.grid(True)
ax1.set_ylim([0.0, 16])
ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax1.bar(matplotlib.dates.date2num(dates), values, color='tab:blue', width=4.0, alpha=0.20, label='Day-by-day')
for tl in ax1.get_yticklabels():
    tl.set_color('tab:blue')

ax2 = ax1.twinx()
ax2.grid(False)
ax2.set_ylim([0.0, 8.0])
ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=False))
ax2.plot_date(matplotlib.dates.date2num(list(rolling_avg.keys())), list(rolling_avg.values()), 'r-', linewidth=0.9, label=f'{days_rolling_avg}-day rolling average')
for tl in ax2.get_yticklabels():
    tl.set_color('r')

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.title(label='Edits over time to Wikipedia article $\it{Russo-Ukrainian}$ $\it{War}$', pad=35)
fig.savefig('figure.png', bbox_inches='tight', pad_inches=0.45)
plt.show()
