# Jena experiment display


![](sources/display.png)


This repository features a script that can be used to animate any kind of numerical information that is related to the different plots of the Jena experiment. You can also save the animation as a video.




### Installation

Clone this repository, create and activate your python environment (conda or virtualenv)  and run this the following command. You should be good to go. 

```
conda env create -f environment.yml 

```


### Basic functionality

By running

```
python display.py --path sources/example_format.csv --what 2
python display.py --path sources/field_diversity.csv --what --static 2 # static case

```
the script will attempt to load the CSV file specified with by "--path", Compute a color range and animate the data. 
You need to specify which column of the CSV file should be displayed. This is done by specifying the index of a column with "--what" 


### Table format

Your table should include a column "datetime" that the specifies the time and a column "plotcode" which specifies the plot. Check "example_format.csv" for further clarification. 



### Additional options

The script comes with a number of options:


Add if you want to display a variable that has no time dimension.
```
 --static
```

Add if you want to average the data over diversity levels.
```
 --averaging
```

Specifies how many different colors are used for the heat map (default =20).
```
 --heat_boxes int
```

Specifies the speed of the animation (Time between frame changes in seconds) (default =0.1).
```
 --speed float
```

Specifices how the plots of the Jena experiment are grouped. "Real" displays the plots in their original layout. "diversity" groups the plots into diversity levels. (default ="real").
```
 --layout diversity/real/block2
```

Specifies the path to the colors that should be used for the heatmap. There are three different color ranges in /heats. You can also create your own ones with e.g. with https://github.com/hihayk/scale and save the color codes to a .txt file
```
 --heat path
```

Add if you want to display the numeric values on the plots.
```
 --display_values
```

Add if you want to prevent the script from caching your table (Cashing speeds up the script when the table is really big).
```
 --no_csv_cash
```

Specifices the color that is used for missing values. Color shold be given in RGB format. Defaults to white (255,255,255).
```
 --nan_color 255 255 255
```

Specifices the lower and uppper boundaries for displaying extreme values. Defaults to (-1.,30.0).
```
 --up_extreme float/int  --low_ extreme float/int
```

Specifices the first and last time step that is animated. If not specified, all data is animated.

```
 --start int   --end int 
```


Add if you want to record your animation. (will be saved under /videos)
```
 --record
```

Specifies the unit that is displayed (Defaults to °C)
```
 --unit str
```



### Example usage

```
cd jena_experiment_display
python display.py --path sources/example_format.csv --what 2 --layout diversity --display_values --nan_color 128 0  256 --up_extreme 4.0 --speed 0.5
```



###### Feel free to contact me if you have any questions. 

