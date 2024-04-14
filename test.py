from src.equatorial.read_lines_and_processed import ReadLinesAndProcessed as ReadLinesAndProcessedEquatorial

pathFile = '/home/eldervivot/Programming/ccbchurch/scrapings/data/enel'
# pathFile = 'data/equatorial'

ReadLinesAndProcessedEquatorial().executeJobMainAsync(pathFile)
