# Load packages
library(ggplot2)
library(devtools)
library(plotly)

# Load data
data = read.csv(file='J:/WDPRO/BPM/Python/google_news_aggregate.csv',
                colClasses=c('NULL', NA, NA, NA, NA))

# Sort data by Flesch
sort.order = data$source[order(data$mean, decreasing=T)]
data$source = factor(data$source, levels=sort.order)

# Remove sources with one headline
data2 = data[data$n_headlines >= 100, ]

# Create a ggplot object
ggnews=ggplot(data2, aes(x=source, y=mean, color=source)) +
    # Add bar graph
    geom_point(shape=19, size=10) +
    # Title graph
    ggtitle('Average Grade Level Readability of News Headlines by Outlet') +
    # Label axes
    ylab('Grade Level') + xlab('News Outlet') +
    # Format theme
    theme(plot.title = element_text(face='bold', size=25),
          axis.title = element_text(face='bold', size=20),
          axis.text.y = element_text(size=16),
          axis.text.x = element_blank(),
          # Hide gridlines
          panel.grid.minor=element_blank(),
          panel.grid.major=element_blank())

# Create a pyplot object
py = plotly(username='jmcontreras', key='nt9c5r1x5u')

# Draw the graph
py$ggplotly(ggnews)