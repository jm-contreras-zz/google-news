# Load packages
library(ggplot2)
library(devtools)
library(plotly)

# Load data
file.name = '/Users/jmcontreras/GitHub/google-news/google_news_aggregate.csv'
col.types = c('NULL', 'character', rep('numeric', 3))
data = read.csv(file=file.name, colClasses=col.types)

# Sort data by Flesch
sort.order = data$outlet[order(data$mean, decreasing=T)]
data$outlet = factor(data$outlet, levels=sort.order)

# Remove sources with one headline
data = data[data$n_headlines >= 100, ]

# Create a ggplot object
ggnews = ggplot(data=data, aes(x=outlet, y=mean, color=outlet)) +
    # Add bar graph
    geom_point(shape=19, size=20) +
    # Title graph
    ggtitle('Average Headline Readability by News Outlet') +
    # Label axes
    ylab('Grade Level') + xlab('News Outlet') +
    geom_errorbar(aes(ymax=mean + sem, ymin=mean - sem), width=0.2) +
    # Format theme
    theme(plot.title = element_text(face='bold', size=25),
          axis.title = element_text(face='bold', size=20),
          axis.text.y = element_text(size=16),
          panel.grid.minor=element_blank(),
          panel.grid.major=element_blank(),
          axis.ticks.x=element_blank())

# Create a pyplot object
py = plotly(username='your_username', key='your_key')

# Draw the graph
py$ggplotly(ggnews)