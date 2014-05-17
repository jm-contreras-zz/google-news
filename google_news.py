# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 21:17:38 2014

@author: jmcontreras
"""

def assess_readability(text):

    # Import module
    from readability.readability import Readability
    
    # Assess grade level    
    return Readability(text).FleschKincaidGradeLevel()

def scrape(file_name):
    
    # Import modules
    from mechanize import Browser
    from lxml.html import fromstring
    from pandas import DataFrame
    from re import search
    from time import strftime
    from os.path import isfile
    
    # Get the current date and time
    date = strftime('%m/%d/%y')
    time = strftime('%H:%M:%S')
    
    # Construct browser object
    browser = Browser()
    
    # Do not observe rules from robots.txt
    browser.set_handle_robots(False)
    
    # Create HTML document
    html = fromstring(browser.open('https://news.google.com/').read())
    
    # Declare outlets and titles
    outlets = html.xpath('.//*[@class="esc-lead-article-outlet-wrapper"]')
    titles = html.xpath('.//*[@class="esc-lead-article-title"]')
    
    # Number of items
    n_items = len(titles)
    
    # Initialize empty Pandas data frame
    empty_list = [None] * n_items
    df = DataFrame({'outlet': empty_list,
                    'title': empty_list,
                    'flesch': empty_list,
                    'date_time': [date + ' ' + time] * n_items})
    
    # Iterate through outlets and titles
    for i in xrange(n_items):
        
        # Declare raw outlet name
        raw_outlet = outlets[i].text_content()
        
        # Find the last meaningful character in the raw_outlet string
        try:
            last_char = raw_outlet.index('-') - 1
        except ValueError as e:
            if e.message == 'substring not found':
                last_char = search('\d', raw_outlet).start()
        
        # Slice the raw outlet name into something useable                
        this_outlet = raw_outlet[:last_char]
        this_title = titles[i].text_content().encode('utf8')

        # Input results into data frame
        df.outlet[i] = this_outlet
        df.title[i] = this_title
        df.flesch[i] = assess_readability(this_title)
    
    # If a file exists, then append results to it; otherwise, create a file
    if isfile(file_name):
        df.to_csv(file_name, header=False, index=False, mode='a')
        report_str = 'Appended '
    else:
        df.to_csv(file_name, index=False)
        report_str = 'Created %s with ' % (file_name)
        
    # Report progress
    print '%s%s headlines on %s at %s' % (report_str, n_items, date, time)

def schedule(file_name, n_jobs, frequency):
    
    # Import modules
    from apscheduler.scheduler import Scheduler
    import logging
    from time import sleep

    # Create a default logger
    logging.basicConfig()

    # Run the first job
    scrape(file_name)

    # Instantiate the scheduler
    sched = Scheduler()
    
    # Start it
    sched.start()

    # Schedule the function
    sched.add_interval_job(scrape, args=[file_name], minutes=frequency,
                           misfire_grace_time=60)
    
    # Wait to run n_jobs (assuming 1 job per hour, which is 3600 seconds)
    sleep(n_jobs * 3600)
    
    # Shutdown the scheduler
    sched.shutdown()
    
def clean(file_name):
    
    # Import modules
    from pandas import DataFrame, isnull
    from re import finditer, search, IGNORECASE
    
    # Read CSV file
    df = DataFrame.from_csv(path=file_name, index_col=False)
    
    # Declare patterns found in dirty news outlet and headline records,
    # including improper encoding
    s_pattern = '\d+ minute|\d+ hour| \(\w+tion\)| \(blog\)'
    t_pattern = '\[video\]| \(\+video\)'
    e_pattern = '\x89\xdb\xd2 '
    
    # Initialize empty list of records to be removed
    remove = []
    
    # Iterate through the records
    for i in xrange(df.shape[0]):
        # Define the news outlet and headline of the iteration
        s = df.outlet[i]
        t = df.title[i].lower()
        # Tag records if the outlet is empty or non-sensical
        if isnull(s) or s == '(multiple names)':
            remove.append(i)
            continue
        # Clean the outlet, if necessary
        if search(s_pattern, s):
            df.outlet[i] = s[:[m.start() for m in finditer(s_pattern, s)][0]]
        # Clean title with encoding error
        if search(e_pattern, t):
            t = t.replace(e_pattern, '')
        # Remove extra letters from Christian Science Monitor name
        if s.endswith('MonitorApr'):
            df.outlet[i] = s[:-3]
        # In titles with plus signs instead of whitespaces, perform replacement
        if t.count(' ') == 0 and t.count('+') > 0:
            df.title[i] = t.replace('+', ' ')
            df.flesch[i] = assess_readability(df.title[i])
        # Remove video references from headlines
        if search(t_pattern, t, IGNORECASE):                
            span = [m.span() for m in finditer(t_pattern, t, IGNORECASE)][0]
            df.title[i] = t[:span[0]] + t[span[1]:]
            df.flesch[i] = assess_readability(df.title[i])
        # Remove information about the time when the article was posted
        if search(' \- Hours', t):
            df.title[i] = t[:[m.start() for m in finditer(' \- Hours', t)][0]]
            df.flesch[i] = assess_readability(df.title[i])
        # Tag records with metadata instead of headlines
        if t.startswith('Written by '):
            remove.append(i)
    
    # Remove unsalvageable records
    df = df.drop(df.index[remove])
    
    # Drop duplicate records
    df['title_lower'] = [t.lower() for t in df.title]
    df.drop_duplicates(cols=['title_lower', 'outlet'], inplace=True)
    df.drop(labels='title_lower', axis=1, inplace=True)
    
    # Save clean data to new file
    df.to_csv(path_or_buf=file_name.replace('.', '_clean.'), index=False)
    
    # Return the DataFrame
    return df

def grades2schools(df):
    
    # Transform each grade to its school equivalent
    df['elem'] = (df.flesch >= 1) & (df.flesch < 6)
    df['middle'] = (df.flesch >= 6) & (df.flesch < 9)
    df['high'] = (df.flesch >= 9) & (df.flesch < 13)
    df['college'] = df.flesch >= 13
    
    # Return the DataFrame
    return df
  
def print_stats(data, stats):
    
    def print_percent(x):
        return round(x.sum() / x.shape[0] * 100, 2)
        
    print '\nFLESCH STATISTICS'
    print 'Mean = %s' % (round(data.flesch.mean(), 2))
    print 'SD   = %s' % (round(data.flesch.std(), 2))
    print 'Min  = %s' % (data.flesch.min())
    print 'Max  = %s' % (data.flesch.max())
        
    print '\nSCHOOL PERCENTAGES'
    print 'Elementary  = %s%%' % (print_percent(data.elem))
    print 'Middle      = %s%%' % (print_percent(data.middle))
    print 'High        = %s%%' % (print_percent(data.high))
    print 'SomeCollege = %s%%' % (print_percent(data.college))
    
    print '\nHEADLINES BY OUTLET'
    print 'Mean = %s' % (round(stats.n_headlines.mean()))
    print 'SD   = %s' % (round(stats.n_headlines.std()))
    print 'Min  = %s' % (stats.n_headlines.min())
    print 'Max  = %s' % (stats.n_headlines.max())
  
def main():
    
    # Import modules
    from numpy import mean
    from scipy.stats import sem
    
    # Name the CSV file
    file_name = 'google_news.csv'
    
    # Schedule and run the scraper
    schedule(file_name=file_name, n_jobs=10, frequency=30)

    # Clean data and save them to a different file
    df = clean(file_name)
        
    # Transform grades to schools (elementary, middle, high, and some college)
    df = grades2schools(df)
    
    # Group items by outlet
    grouped = df.groupby(by='outlet', as_index=False)
    
    # Compute aggregate Flesch statistcs
    flesch_dict = {'mean': mean, 'sem': sem, 'n_headlines': len}
    flesch_stats = grouped['flesch'].agg(flesch_dict)
    
    # Restrict news outlets to those with at least 100 headlines
    flesch_stats = flesch_stats[flesch_stats.n_headlines >= 100]
    
    # Apply the same restriction to the non-aggregated data
    df = df[df.outlet.isin(list(set(flesch_stats.outlet)))]
    
    # Print statistics
    print_stats(data=df, stats=flesch_stats)
    
    # Save aggregated data
    flesch_stats.to_csv('google_news_aggregate.csv')
    
    # Plot results
    from subprocess import call
    Rscript = '/Library/Frameworks/R.framework/Versions/3.0/Reoutlets/Rscript'
    call([Rscript, '/Users/jmcontreras/Github/google-news/google_news.R'])
    
if __name__ == '__main__':
    
    main()