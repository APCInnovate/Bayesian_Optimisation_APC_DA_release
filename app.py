############# Shiny for Python Template ###################################
# First draft run through, to set up the dashboard to look as similar to the R Shiny applications as possible.
from pathlib import Path
from datetime import datetime
from shiny import App, ui, render, reactive, req
from shiny.types import ImgData, FileInfo
import os
from faicons import icon_svg
import sys
#################### Add additional libraries below here ##################

import pandas as pd #Used for creating data frames
import plotly.io as pio #Used for plotting and visualising produced data
import plotly.tools as tls
import numpy as np
from shinywidgets import output_widget, render_widget  
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'obsidian')))
from obsidian import Campaign, ParamSpace, Target, BayesianOptimizer #The core components of conducting a Bayesian Optimisation 
from obsidian.parameters import Param_Categorical, Param_Continuous, Param_Discrete_Numeric, Param_Ordinal #Bring in the types of parameters we want
from obsidian.optimizer import BayesianOptimizer
from obsidian.plotting import surface_plot, MDS_plot, parity_plot
from obsidian.plotting import plot_interactions as obs_plot_interact
from obsidian.plotting import optim_progress as obs_optim_progress
from obsidian.plotting import factor_plot as obs_factor_plot
#from obsidian.experiment import ExpDesigner
from obsidian.campaign import Explainer
#import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from pathlib import Path
 
#################### Set ggplot theme (not started yet) ###################

#################### Resource Directories #################################
# If all files included in the www folder no need to modify 
resource_dir = Path(__file__).parent / "www"

#################### Web App Version ######################################
Web_app_version = "Version: 0.0.0"
###########################################################################
app_ui = ui.page_fillable(
#################### Template Specific Styling ############################
#################### Do Not Edit ##########################################
    ui.tags.link(
    rel="stylesheet",
    href="https://fonts.googleapis.com/css2?family=Montserrat"
    ),
    ui.tags.link(
     rel="stylesheet",
     href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        ),
        ui.tags.link(
            rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        ),# for remove
    ui.tags.link(
     rel="stylesheet", 
     href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
        ), 
    ui.tags.style(
    "body { font-family: 'Montserrat'}"
    ),
    ui.tags.link(href= "www/style.css", rel="stylesheet"),
    ui.tags.style(
         ".card-header {border-bottom: 2px solid #3BAFDA; border-top:4px solid #3BAFDA}"
    ),
#################### Set application header (do not edit) #################

    ui.panel_title(
        ui.div(
            
        ui.output_image("app_title_id", height="100%")),
        ),
###########################################################################        
    ui.layout_sidebar(
            ui.sidebar(
     ############### Set up meni items - edit as needed ###################
     # other options for icons can be found at https://getbootstrap.com/docs/3.4/components/#glyphicons or at https://fontawesome.com/icons will likely need additional styling css
                ui.input_radio_buttons("menu_selection_id", "",  choices = {
                     "dashboard":ui.HTML('<span class="glyphicon glyphicon-file"></span> Parameter Space '),
                     "results":ui.HTML('<i class="fa-solid fa-gear"></i> Model Configuration'),
                     "results_tab_id":ui.HTML('<i class="fa-solid fa-pen"></i> Results Visualisations'),
                     "informtion_tab_id":ui.HTML('<i class="fa-solid fa-file"></i> User Information'),
     ######################################################################

     ############### Feedback Section - for internal apps only, otherwise delete this section ####                
                     "feed_back_tab_id":ui.HTML('<i class="fas fa-comment-dots"></i> WebApp Feedback')
     ######################################################################                
                }),
                # Adjust sidebar width as needed
                width = 230            
            ),
     ############### Full UI setup handled in linked section below ########       
            ui.output_ui("main_panel")
        ),
     ############### Application Footer (do not edit) #####################
    ui.row(
            ui.column(6, ui.output_ui("copyright_company_URL_id")),
            ui.column(2, ui.output_text("Version_track_id"), offset=4, style="text-align:right;")
        )      
)


def server(input, output, session):
    ################ Loading iAchieve Logo (do not edit) ##################
    @render.image  
    def app_title_id():
        img_file = resource_dir / "iAchieve_Logo.png"
        return {"src": img_file, "style" :"width:230px;"} 
    
    
     ############### Main UI linked above #################################
    @output
    @render.ui
    def main_panel():
         selection = input.menu_selection_id()
         if selection == "dashboard":
              return ui.page_fluid(
                  ui.layout_columns(
                                        #Card 1 will have the Upload Excel Button and the number of each form of variables
                                        ui.card(
                                                ui.card_header(ui.h4("Please upload your experiments and determine the types of factors in it")),
                                                ui.layout_columns(
                                                                    ui.card(
                                                                         
                                                                            ui.input_file(
                                                                              "experiment_upload", "Please Choose your Execl file", accept =  [".xlsx"], multiple = False
                                                                                      )
                                                                            ),

                                                                    ui.card(
                                                                         
                                                                            ui.output_ui("objective_decision"),
                                                                            ui.card(
                                                                                ui.input_action_button("confirm_objective", "Confirm Objective(s)", disabled = True),
                                                                                ui.input_action_button("remove_objective", "Restart ", disabled = True)
                                                                            ),
                                                                    width=1 / 2,
                                                                            ),
                                                                    ),
                                                    ),

                                        #This will contain the dataframe with imported results 
                                        ui.card(
                                                ui.card_header(ui.h4("Raw Data")),
                                                ui.output_table("raw_frame")
                                        ),
                                        
                                        col_widths=(6, 6),
                                    ), 
                    ui.layout_columns(
                                        ui.card(
                                                ui.card_header(ui.h4(ui.output_text("chosen_factor"))), 
                                                ui.card (ui.input_select(  
                                                                    "selected_factor",  
                                                                    "Choose Factor Category:",  
                                                                    {"Num_cont": "Numerical Continous", "Num_Disc" : "Numerical Discrete" ,"Cat": "Categorical", "Ord": "Ordinal"},  
                                                                    multiple=False, 
                                                                    width= '600px'
                                                                )),
                                                ui.output_ui("selected_output"),
                                                ui.output_ui("text_boxes"),
                                                ui.card(ui.input_action_button("append_button", "Append", disabled = True)),
                                                # ui.layout_columns(
                                                #                     #ui.card(ui.input_action_button("delete_button", "Previous Data", disabled = True)),
                                                #                     ui.card(ui.input_action_button("append_button", "Append", disabled = True)), 
                                                #                     col_widths=(6,6)
                                                # )
                                                 
                                        ), 

                                        ui.card(    
                                                    ui.card_header(ui.h4("Parameter Space Design")),
                                                    ui.output_data_frame("counter"), 
                                                    ui.input_action_button("param_final", "Finalise Data Inputs", disabled= True)
                                                ), 

                                        col_widths=(6,6)
                    ), 
                   
            )
         elif selection == "results":
              return ui.page_fluid(
                                    ui.card(    ui.card_header(ui.h4("Define the configuration", style="color: #12375b;font-weight:bold;")),  
                                                ui.input_select(  
                                                                    "selected_config",  
                                                                    "Please choose which coniguration is required",  
                                                                    {"No_data": "Initial Sampling Required", "Model_training" : "Train Model with Data" },  
                                                                    multiple=False, 
                                                                    width= '600px'
                                                                )  
                                                ), 
                        
                                    ui.output_ui("objective_menu"),

                                    ui.card(
                                            ui.output_ui("config_menu"),
                                            ui.output_ui("advanced_config_menu"),
                                            ui.output_ui("model_config"),
                                            ),
                                    
                                    ui.card(
                                            ui.output_ui("results_menu"),
                                            ui.output_ui("results_output"), 
                                            ui.download_button("results_download", "Download Results Table", disabled= False), 
                                    ),
                    )
         

     ############### Submit Feedback - for internal apps only #############
         elif selection == "feed_back_tab_id":
              return ui.div(
                   ui.card(
                        ui.card_header(ui.h3("WebApp Feedback", style="color: #12375b;font-weight:bold;")),
                        ui.p("If you encounter an issue or have suggestions for how to improve this WebApp, please fill in the form below and click Submit. THis will open a prepared email, for you to send. Thank you!"),
                        ui.input_select(id = "feedback_type_id",label = "Please select:",choices=[ "Report an Issue", "Log a Suggestion"], multiple=False, width="25%"),
                        ui.input_text(id = "feedback_webapp_name_id", label = "Provide the WebApp name:", value= "", width = "50%"),
                        ui.row(
                            ui.column(9,
                                 ui.input_text_area(id = "feedback_details_id", label= "Describe the Issue or Suggestion:", value = "", width = "100%", height="140px" )
                            ),
                            ui.column(3,
                                      ui.output_ui(id = "submit_feedback_ui_id")
                                      )     
                        )
                   )
            ), 
         elif selection == "results_tab_id":
                return ui.div(
                    ui.card( ui.card_header(ui.h3("Plotting and Visualisation", style="color: #12375b;font-weight:bold;")),

                            ui.card(
                                    ui.card_header(ui.h5("Produce Surface Plot(s)", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("surface_plot_decision", "Yes", True),
                                    ui.output_ui("surface_plot_options"), 
                                    ui.output_ui("surface_plot_second_choice"), 
                                    ui.output_ui("surface_plot_result_choice"), 
                                    output_widget("surface_plot_done")
                            ), 

                            ui.card(
                                    ui.card_header(ui.h5("Produce Factor Plot(s)", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("factor_plot_decision", "Yes", False),
                                    ui.output_ui("factor_plot"),
                                    output_widget("factor_plot_done")
                            ), 

                            ui.card(
                                    ui.card_header(ui.h5("Graph Optimisation Progress", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("optim_plot_decision", "Yes", False),
                                    output_widget("optim_progress"),
                            ), 

                            ui.card(
                                    ui.card_header(ui.h5("Produce Shapley Values", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("shapley_plot_decision", "Yes", False),
                                    ui.output_plot("shap_values"),
                                    ui.output_ui("download_shapley_button")
                            ), 

                            ui.card(
                                    ui.card_header(ui.h5("Produce Multidimensional Scaling Plot", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("mds_plot_decision", "Yes", False),
                                    ui.output_ui("MDS_plot_choice"),
                                    output_widget("create_MDS_plot")
                            ), 


                            ui.card(
                                    ui.card_header(ui.h5("Produce Parity Plot", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("parity_plot_decision", "Yes", False),
                                    ui.output_ui("parity_plot_choice"),
                                    output_widget("parity_plot_done")
                            ), 

                            ui.card(
                                    ui.card_header(ui.h5("Produce Parameter Interaction Matrix", style="color: #12375b;font-weight:bold;")),
                                    ui.input_checkbox("param_matrix_decision", "Yes", False),
                                    ui.output_plot("parameter_interaction_matrix"), 
                                    ui.output_ui("download_param_button")
                                    
                            )

                    )

                ), 
         elif selection == "informtion_tab_id" : 
             return ui.div(
                 ui.navset_pill(
                            ui.nav_panel("Using the WebApp", ui.tags.iframe(src = "Test.pdf", style="width: 100%; height: 100vh; border: none;" ) ), 
                            ui.nav_panel("Intrepreting the Results", ui.tags.iframe(src = "Test.pdf", style="width: 100%; height: 100vh; border: none;" )), 
                            ui.nav_panel("Bayesian Optimisation Theory", ui.tags.iframe(src = "Test.pdf", style="width: 100%; height: 100vh; border: none;" ))
                 )
             ), 
###################################################################################################
    
    ############### Beginning the calculations and background functions required ###############
    
    # Initialize reactive Vals
    data_val = reactive.Value(None)
    param = reactive.Value([])
    edited_frame = reactive.Value(pd.DataFrame())
    compiled_frame = reactive.Value(pd.DataFrame())
    formatted_Frame = []
    objectives = []
    next_suggest = reactive.Value(pd.DataFrame())
    Campaign_information = reactive.Value(pd.DataFrame())
    explained = reactive.Value(pd.DataFrame())

    ############### Uploading results & reading/visualising the raw data frame ###############

    @reactive.calc
    def read_file():
            experiment_upload: list | None = input.experiment_upload()            
            if experiment_upload is None:
                return pd.DataFrame() 

            return pd.read_excel(experiment_upload[0]["datapath"])
    
    @reactive.Effect
    def update_data_val():
        experiment_upload = input.experiment_upload()
        
        if experiment_upload is None:
            data_val.set(pd.DataFrame())  
            return
        
        all_param = pd.read_excel(experiment_upload[0]["datapath"])

        #file_path.append(experiment_upload[0]["datapath"])
        #print(file_path)
        
        # Drop the "Iteration" column if it exists
        cleaned_data = all_param.drop(columns=["Iteration"], errors="ignore")
        
        # Store the cleaned data in data_val
        data_val.set(cleaned_data)


    @output(id="raw_frame")
    @render.table
    def raw_frame():
        initial_parameters = data_val.get()

        if initial_parameters is None:
            return pd.DataFrame(({"Message": ["No data loaded"]}))
        
        #param_count = initial_parameters.shape[1]
        #param_names = initial_parameters.columns.tolist()

        parameter_frame = pd.DataFrame(
            initial_parameters
        )

        #ui.update_action_button("delete_button", disabled = False)
        ui.update_action_button("append_button", disabled = False)
        
        return parameter_frame
    

    @output 
    @render.ui
    def objective_decision():

        all_param = data_val.get()

        if all_param is None:
            return f"⚠! No data has been loaded! "
        
        column_names = all_param.columns.to_list()
        column_length = len(column_names)

        ui.update_action_button("confirm_objective", disabled = False)
        
        return [ui.input_checkbox_group("checkbox", "Please select your objective factors",  {column_names[i] : column_names[i] for i in range(column_length) } )]

    @reactive.effect
    @reactive.event(input.confirm_objective)
    def update_buttons():
        req(input.confirm_objective())
        
        initial_parameters = (data_val.get()).copy()
        edited_frame.set(initial_parameters)
        frame_editing = edited_frame.get()

        columns_to_remove = input.checkbox()

        for col in columns_to_remove:
            if col in frame_editing.columns:
                frame_editing.pop(col)

        print(edited_frame())

        ui.update_action_button("confirm_objective", disabled = True)
        ui.update_action_button("remove_objective", disabled = False)

    @reactive.effect
    @reactive.event(input.remove_objective)
    def delete_button_update():
        req(input.remove_objective())
        
        initial_parameters = (data_val.get()).copy()
        edited_frame.set(initial_parameters)

        print(edited_frame())

        ui.update_action_button("confirm_objective", disabled = False)
        ui.update_action_button("remove_objective", disabled = True)

    ############### Allowing the user to sepcify the upper/lower bounds or categories of the param space ###############
   
    @output
    @render.ui
    def selected_output():
        selected_values = input.selected_factor()
        if selected_values == "Num_cont":
             return ui.card(
                  ui.input_numeric("lower_bound_cont", "Lower Bound", 0.0000001, min=-100000000000000, max=100000000000000),
                  ui.input_numeric("upper_bound_cont", "Upper Bound", 0.0000001, min=-100000000000000, max=100000000000000)
             )
        elif selected_values == "Num_Disc":
            return ui.card(
                  ui.input_numeric("disc_no", "Number of Discrete Points", 1, min=1, max=10)
             )
        elif selected_values == "Cat":
             return ui.card(
                   ui.input_numeric("cat_no", "Number of Categories", 1, min=1, max=5)
             )
        elif selected_values == "Ord":
             return ui.card(
                  ui.input_numeric("ord_no", "Number of Ordinal Options", 1, min= 1, max=5)
             )
        else :
             return ui.card(
                  "No Options have been chosen "
             )
        

             
###################################################################################################
    
    @output
    @render.ui
    def text_boxes():
        selected_values = input.selected_factor()
        if selected_values == "Cat" : 
            return [ui.input_text(f"factor_{i}", f"Categorical Data {i+1}") for i in range(input.cat_no())]
        elif selected_values == "Ord":  
            return [ui.input_text(f"factor_{i}", f"Ordinal Data {i+1}") for i in range(input.ord_no())]
        elif selected_values == "Num_Disc" : 
            return [ui.input_text(f"factor_{i}", f"Discrete Data {i+1}") for i in range(input.disc_no())]
        else :
            return None
        
    
    def join_categorical():

        selected_values = input.selected_factor()
        if selected_values == "Cat" : 
            values = [input[f"factor_{i}"]() for i in range(input.cat_no())]
            return " , ".join(values)
        elif selected_values == "Ord":  
            values = [input[f"factor_{i}"]() for i in range(input.ord_no())]
            return ", ".join(values)
        elif selected_values == "Num_Disc": 
            values = [input[f"factor_{i}"]() for i in range(input.disc_no())]
            return " , ".join(values)
        else :
            return None
        # Collect and display entered text values


###################################################################################################

    def factor_properties():
        
        selected_values = input.selected_factor()
        
        if selected_values == "Num_cont":
            
            category = "Numerical Continous"
            lower_bound = input.lower_bound_cont()
            upper_bound = input.upper_bound_cont()

            Data_point = [category, upper_bound, lower_bound]
            
            return Data_point
        
        elif selected_values == "Num_Disc":
            
            category = "Numerical Discrete"
            num_disc_no = input.disc_no()
            num_disc_data = join_categorical()

            Data_point = [category, num_disc_no, num_disc_data]
            
            return Data_point
        elif selected_values == "Cat":
            
            category = "Categorical"
            cat_no = input.cat_no()
            cat_data = join_categorical()

            Data_point = [category, cat_no, cat_data]
            
            return Data_point
        elif selected_values == "Ord":
            
            category = "Ordinal"
            ord_no = input.ord_no()
            ord_data = join_categorical()

            Data_point = [category, ord_no, ord_data]
            
            return Data_point
        else :
            return "No data chosen"
    
    @output
    @render.data_frame
    @reactive.event(input.append_button)
    def counter():
        
        initial_parameters = edited_frame.get()
        
        parameter_frame = pd.DataFrame(initial_parameters)
        
        Data_point = factor_properties()

        current_params = param.get()
        current_params.append(f"{input.append_button()}")
        param.set(current_params)
        
        current_frame = compiled_frame.get()
        data_name = initial_parameters.columns[len(current_params) - 1]
        current_frame.insert(len(current_params) - 1, f"{data_name}", Data_point)
        compiled_frame.set(current_frame)

        if len(current_params) >= parameter_frame.shape[1]:
            ui.update_action_button("append_button", disabled=True)
            ui.update_action_button("param_final", disabled=False)

        return current_frame
    

    @output 
    @render.text
    def chosen_factor():
        all_param = edited_frame.get()

        if all_param is None or not isinstance(all_param, pd.DataFrame) :  #or all_param.empty:
            return 'Please upload a Excel file to begin defining your parameter space'

        current_params = param.get()

        if len(current_params) >= (all_param.shape[1] ):
            return "Parameter Space Refinement should be concluded"

        # This triggers re-evaluation when button is clicked
        if reactive.event(input.append_button):
            if input.append_button() > len(current_params):  
                current_params.append("new_param")  
                param.set(current_params)


        # Make function reactive to button clicks
        input.append_button()  

        if len(current_params) < all_param.shape[1]:
            data_name = all_param.columns[len(current_params)]
            return f"Please define the details of the current Factor: {data_name}"
        else:
            return "Parameter Space Refinement should be concluded"

    @reactive.effect
    @reactive.event(input.param_final)
    def param_space_creation():
                
        i = 0 
        space_frame = compiled_frame.get() 
        space_length = space_frame.shape[1]
        column_names = space_frame.columns.to_list()
        
        print(space_frame) #Test to see framme
        print(space_length) #Test to ensure correct length 
        print(column_names) #Test to ensure correct column names
        
        #Read the Property Type 
        factor_type = (space_frame.iloc[0]).values
        upper_bound = (space_frame.iloc[1]).values
        lower_bound = (space_frame.iloc[2]).values
        
        print(factor_type)


        #Loop 
        while i < space_length: 

            #Read the Type of property 

            if factor_type[i] == "Numerical Continous":
                #print(f"The factor {column_names[i]} is contionus")
                factor = Param_Continuous(column_names[i], upper_bound[i], lower_bound[i])
                formatted_Frame.append(factor)
            elif factor_type[i] == "Numerical Discrete":
                print(f"The factor {column_names[i]} is discrete")
                #factor = Param_Ordinal(column_names[i], upper_bound[i], lower_bound[i])
                int_list = [int(x.strip()) for x in lower_bound[i].split(',')]
                factor = Param_Discrete_Numeric(column_names[i], int_list) 
                formatted_Frame.append(factor)
            elif factor_type[i] == "Categorical":
                #print(f"The factor {column_names[i]} is categorical")
                factor = Param_Categorical(column_names[i], lower_bound[i])
                formatted_Frame.append(factor)
            elif factor_type[i] == "Ordinal":
                #print(f"The factor {column_names[i]} is ordinal")
                factor = Param_Continuous(column_names[i], lower_bound[i]) 
                formatted_Frame.append(factor)
            i = i+1
        print(formatted_Frame)


###################################################################################################

    @output
    @render.ui
    def config_menu():
        
        config_data = input.selected_config()

        if config_data == "No_data":
            return ui.card(    
                                                ui.card_header(ui.h5("Before continuing ensure your inputs and parameter space are formatted correctly", style="color: #12375b;font-weight:bold;")),
                                                ui.input_numeric("samples", "Number of Initial Experiments to be preformed", 1, min=1, max=15),
                                                ui.input_select("sample_config", "Select a sampling method", {"LHS":"Latin Hypercube Sampling", "Random":"Random", "Sobol":"Sobol"}), 
                                                ui.input_action_button("sample_begin", "Begin Sampling"),
                    )
                            
        
        elif config_data == "Model_training":
            return ui.card(    
                                            ui.card_header(ui.h5("Before continuing ensure your inputs and parameter space are formatted correctly", style="color: #12375b;font-weight:bold;")), 
                                            ui.input_numeric("exp_recommend", "How many experiment recommendations do you require?", 5, min=5, max=15),
                                            ui.input_switch("advanced_config", "Activate Advanced Configurations", False),
                            )
    @output
    @render.ui
    def model_config():
        config_data = input.selected_config()
        
        if config_data == "No_data":
            return None 
        
        elif config_data == "Model_training":
            return ui.card(
                ui.input_action_button("experiment_recommendations", "Initialise Recommending Process", disabled = False)
            )

    @output
    @render.ui 
    def objective_menu():
    
            initial_parameters = (data_val.get()).copy()
            edited_frame.set(initial_parameters)
            objective_frame = (edited_frame.get()).copy()

            #Filter - only the objective data is listed everything else removed

            objective_decision = list(input.checkbox())
            objective_frame = objective_frame[objective_decision]
            objectives.extend(objective_decision)

            return ui.card(
            ui.card_header(ui.h4("Define the response parameters goals", style="color: #12375b;font-weight:bold;")),
            [ui.input_select(objective_decision[i], objective_decision[i], {"max":"Maximise", "min":"Minimise"}) for i in range(len(objective_decision))]
            ) 
        
        
        
    @reactive.effect
    def intial_warning():
        sampling = input.sample_config()

        if sampling == "LHS" :                    
            return None
    
        else:
            ui.notification_show(
                                    "⚠ Warning! Latin Hypercube Sampling is the recommended approach, only change if strictly required", 
                                    type = "warning", duration = 5,
            )
            return None

    @output
    @render.ui
    def advanced_config_menu():
        
        advanced_config = input.advanced_config()

        if advanced_config == True :
            
            ui.notification_show(
                                    "⚠ Warning! Advanced configuration should only be used by certain users do not adjust settings unless able to do so", 
                                    type = "warning", duration = 5,
            )

            return ui.card( 
                            ui.input_select("surrogate_config", "Select the surrogate function", {"Default":"Default", "GP":"Guassian Process", "MixedGP":"Mixed Gaussian Process", "DKL":"Deep Kernel Learning", "DNN":"Dropout Neural Network"}),
                            ui.input_select("acquistion_config", "Select the acquisiton function", {"Default":"Default", "EI":"Expected Improvement", "NEI":"Noisy Expected Improvement", "PI":"Probability of Improvement", "UCB":"Upper Confidence Bound", "SR":"Simple Regret", "EHVI":"Expected Hypervolume Improvement", "NEHVI":"Noisy Expected Hypervolume Improvement", "NIPV":"Ngeative Integrated Posterior Variance", "Mean":"Mean", "SF": "Space Fill"}),
            )
        else : 
           return None
        
    @reactive.effect
    def intial_warning():
        surrogate = input.surrogate_config()

        if surrogate == "Default" :                    
            return None
    
        else:
            ui.notification_show(
                                    "⚠ Warning! Change from default surrogate function is not recommended!", 
                                    type = "warning", duration = 5,
            )
            return None
        
    @reactive.effect
    def intial_warning():
        acquistion = input.acquistion_config()

        if acquistion == "Default" :                    
            return None
    
        else:
            ui.notification_show(
                                    "⚠ Warning! Change from default acquistion function is not recommended!", 
                                    type = "warning", duration = 5,
            )
            return None
    
    @reactive.effect
    @reactive.event(input.sample_begin)
    def sampling_begin():
        
        print("Begin sample")
        
        target = []
        i = 0
        X_space = ParamSpace(formatted_Frame)
        no_samples = input.samples()
        config = input.sample_config()

        #Iteraively acccess the select choice and the name of the variable then create target and add to target list
        while i < (len(objectives)): 
            
            #Access the name i.e. objectives[i]
            object_target = objectives[i]
            print(object_target)
            
            #Access the input i.e. input.objectives[i]
            information = input[object_target]()
            print(information)

            #Create this as a Target
            goal = Target(object_target, aim = information)

            #Add the Target to the target list 
            target.append(goal)
            
            i = i + 1 
        
        campaign = Campaign(X_space, target, seed = 702)
        X0 = campaign.initialize(m_initial = no_samples, method = config)
        
        Campaign_information.set(campaign)

        print(X0)
        next_suggest.set(X0)
        
        return 
    
    @reactive.effect
    @reactive.event(input.experiment_recommendations)
    def obsidian_campaign(): 
            
            target = []
            i = 0
            X_space = ParamSpace(formatted_Frame)

            #Iteraively acccess the select choice and the name of the variable then create target and add to target list
            while i < (len(objectives)): 
                
                #Access the name i.e. objectives[i]
                object_target = objectives[i]
                print(object_target)
                
                #Access the input i.e. input.objectives[i]
                information = input[object_target]()
                print(information)

                #Create this as a Target
                goal = Target(object_target, aim = information)

                #Add the Target to the target list 
                target.append(goal)
                
                i = i + 1 

            print(type(target))
            results = read_file()
            print(type(results))

            advanced_config = input.advanced_config()
            print(advanced_config)

            if advanced_config == True:
                
                #acquistion_choice = input.acquistion_config()
                surrogate_choice = input.surrogate_config()
                
                if surrogate_choice == "Default":

                    campaign = Campaign(X_space, target, seed = 702)
                
                else:

                    test = BayesianOptimizer(X_space, surrogate= surrogate_choice)
                    campaign = Campaign(X_space, target, optimizer= test, seed = 702)
            else: 
                campaign = Campaign(X_space, target, seed = 702)          
            
            campaign.add_data(results)
            campaign.fit()
            
    
            if advanced_config == True : 

                acquistion_choice = input.acquistion_config()
                print(acquistion_choice)
                print(type(acquistion_choice))

                if acquistion_choice == "Default":
                    X_suggest, eval_suggest = campaign.suggest(m_batch = input.exp_recommend())
                else:
                    X_suggest, eval_suggest = campaign.optimizer.suggest(acquisition = [acquistion_choice], m_batch = input.exp_recommend())
            else: 
                print("Beginning X_Suggest Process : No Advanced Config")
                X_suggest, eval_suggest = campaign.suggest(m_batch = input.exp_recommend())
            
            Campaign_information.set(campaign)
            
            print(X_suggest)
            next_suggest.set(X_suggest)
            
            exp = Explainer(campaign.optimizer)
            explained.set(exp)
            
            return 

    @output
    @render.ui
    def results_menu():
        
        config_data = input.selected_config()
        
        if config_data == "No_data":
            #ui.update_action_button("results_download", disabled= False)
            return ui.card_header(ui.h4("Sampling Process Results using : ", style="color: #12375b;font-weight:bold;"))
        
        else: 
            #ui.update_action_button("results_download", disabled= False)
            return ui.card_header(ui.h4("Recommended set of experiments to conduct : ", style="color: #12375b;font-weight:bold;"))



    @render.table
    def results_output():
        
        results = next_suggest.get()
        information = Campaign_information.get()

        if results is None or results.empty:
            return pd.DataFrame(({"Message": ["No Results have been loaded"]}))

        results_frame = pd.DataFrame(
            results
        )

        results_Frame_rounded = results_frame.round(2)
        #print(results_Frame_rounded)
        
        return results_Frame_rounded
    
    @output
    @render.ui
    def surface_plot_options():

        #Read in the user choice of whether or not they want a surface plot
        choice = input.surface_plot_decision()
        results = next_suggest.get()
        
        if choice == True:

            if results is None or results.empty:
                return "No information available - please check your case for errors"
            
        #Produce a drop down list containing all the factors 
            factors = compiled_frame.get()
            factor_names = list(factors.columns)

            return [ui.input_select("surface_plot_option_1", "Select the factor to plot on the X-Axis",  {factor_names[i]: factor_names[i] for i in range(len(factor_names))} )]
        else: 
            return None


    
    @output
    @render.ui
    def surface_plot_second_choice():

        #Read in the user choice of whether or not they want a surface plot
        choice = input.surface_plot_decision()
        results = next_suggest.get()
        option_1 = input.surface_plot_option_1()

        if choice == True:

            if results is None or results.empty:
                return None
            
        #Produce a drop down list containing all the factors 
            factors = compiled_frame.get()
            factor_names = list(factors.columns)
            factor_names.remove(option_1)
            modified_names = factor_names


            return [ui.input_select("surface_plot_option_2", "Select the factor to plot on the Y-Axis",  {modified_names[i]: modified_names[i] for i in range(len(modified_names))} )]
        else: 
            return None
    
    @output
    @render.ui
    def surface_plot_result_choice():
        
        choice = input.surface_plot_decision()
        results = next_suggest.get()

        if choice == True:

            if results is None or results.empty:
                return None

            response_names = list(input.checkbox())

            return [
                ui.input_select("surface_plot_option_3", "Select the Response to visualise", {response_names[i]: response_names[i] for i in range(len(response_names))} ), 
                ui.input_action_button("surface_plot", "Plot Response Surface")
                ]
        else:
            return None

    @render_widget 
    @reactive.event(input.surface_plot)
    def surface_plot_done():

        #Depending on the user choice match to the feature IDs -- i.e. create a list matching every feature to a number 
        factors = compiled_frame.get()
        campaign = Campaign_information.get()

        factor_names = list(factors.columns)
        factor_ids = {factor_names[i] : [i] for i in range(len(factor_names))}

        print(factor_ids)

        response_names = list(input.checkbox())
        response_ids = {response_names[i] : [i] for i in range(len(response_names))}

        print(response_ids)

        selection_1 = input.surface_plot_option_1()
        print(selection_1)

        selection_2 = input.surface_plot_option_2()
        print(selection_2)
        
        selections = [selection_1, selection_2]
        response_chosen = input.surface_plot_option_3()

        selection_ids = [factor_ids[factors] for factors in selections]
        print(selection_ids)
        selection = tuple(x[0] for x in selection_ids)
        print(selection)

        response = int(response_ids.get(response_chosen)[0]) #Select the first value in the list i.e. the matchin response ID and convert to integer

        #Debugging Tests
        #print(selection_ids)
        print(response)

        return surface_plot(campaign.optimizer, feature_ids=selection, response_id=response )

    
    @render.plot
    @reactive.event(input.shapley_plot_decision)
    def shap_values():
        
        #Read in the user choice of whether or not they want a surface plot
        choice = input.shapley_plot_decision()
        results = next_suggest.get()
        
        if choice == True:

            if results is None or results.empty:
                return "No information available - please check your case for errors"
            
            exp = explained.get()
            exp.shap_explain() #Define Response ID that we want , specify iterations 
            
            print(type(exp.shap_explain()))
            print(type(exp.shap_summary()))

            #plotly_fig = tls.mpl_to_plotly(fig) 
        
            return exp.shap_summary()
        else: 
            return None
        
    @render.ui
    @reactive.event(input.shapley_plot_decision)
    def download_shapley_button():
        choice = input.shapley_plot_decision()

        if choice == True: 
            return ui.download_button("download_shapley_figure", "Download Produced Shapley Plot")
        else: 
            return None
        
    @render.download(filename="Shapley_Plot.png")
    def download_shapley_figure():
        results = next_suggest.get()

        exp = explained.get()
        exp.shap_explain() #Define Response ID that we want , specify iterations 

        fig = exp.shap_summary()
        with io.BytesIO() as buf:
            fig.savefig(buf, format="png", bbox_inches='tight')
            yield buf.getvalue()
    

    @render.ui
    @reactive.event(input.factor_plot_decision)
    def factor_plot():
        
        choice = input.factor_plot_decision()
        results = next_suggest.get()

        if choice == True:

            if results is None or results.empty:
                return None

            response_names = list(input.checkbox())
            factors = compiled_frame.get()
            factor_names = list(factors.columns)

            return [
                ui.input_select("factor_plot_option", "Select the factor to plot on the X-Axis",  {factor_names[i]: factor_names[i] for i in range(len(factor_names))} ),
                ui.input_select("factor_plot_response", "Select the Response to visualise", {response_names[i]: response_names[i] for i in range(len(response_names))} ), 
                ui.input_action_button("factor_plot_create", "Create Factor Plot"),
                ]
        else:
            return None
        
    @render_widget  
    @reactive.event(input.factor_plot_create)
    def factor_plot_done():

        #Depending on the user choice match to the feature IDs -- i.e. create a list matching every feature to a number 
        factors = compiled_frame.get()
        campaign = Campaign_information.get()

        factor_names = list(factors.columns)
        factor_ids = {factor_names[i] : [i] for i in range(len(factor_names))}

        response_names = list(input.checkbox())
        response_ids = {response_names[i] : [i] for i in range(len(response_names))}

        selection = input.factor_plot_option()

        response_chosen = input.factor_plot_response()

        selected = int(factor_ids.get(selection)[0])
        response = int(response_ids.get(response_chosen)[0]) #Select the first value in the list i.e. the matchin response ID and convert to integer

        #fig = obs_factor_plot(campaign.optimizer, feature_id=selected, response_id=response)
        #print(type(fig))

        #Potentially pull out the numerical values for the 95% prediction band 
        
        return obs_factor_plot(campaign.optimizer, feature_id=selected, response_id=response) #Has to be defined as shiny also has a Factor_plot function
    
    @render_widget
    @reactive.event(input.optim_plot_decision)
    def optim_progress():

        #Read in the user choice of whether or not they want a surface plot
        choice = input.optim_plot_decision()
        results = next_suggest.get()
        campaign = Campaign_information.get()

        if choice == True:

            if results is None or results.empty:
                return "No information available - please check your case for errors"
            
            figure = obs_optim_progress(campaign)
            
            return figure 
        
        else: 
            return None
        


    @output
    @render.ui
    def MDS_plot_choice():

        #Read in the user choice of whether or not they want a surface plot
        choice = input.mds_plot_decision()
        results = next_suggest.get()
        information = Campaign_information.get()

        if choice == True:

            if results is None or results.empty:
                return "No information available - please check your case for errors"
        
            return [ui.input_action_button("MDS_plot_create", "Create Multidimensional Scaling Plot")]
            
        else: 
            return None
        
    @render_widget  
    @reactive.event(input.MDS_plot_create)
    def create_MDS_plot():
        campaign = Campaign_information.get()

        fig = MDS_plot(campaign)

        return fig
    
    @output
    @render.ui
    def parity_plot_choice():

        #Read in the user choice of whether or not they want a surface plot
        choice = input.parity_plot_decision()
        results = next_suggest.get()
        information = Campaign_information.get()

        if choice == True:

            if results is None or results.empty:
                return "No information available - please check your case for errors"
            
            response_names = list(input.checkbox())
            
            return [
                ui.input_select("parity_plot_response", "Select the Response to visualise", {response_names[i]: response_names[i] for i in range(len(response_names))} ),
                ui.input_action_button("parity_plot_create", "Create Multidimensional Scaling Plot")
                ]
            
        else: 
            return None
        
    @render_widget  
    @reactive.event(input.parity_plot_create)
    def parity_plot_done():
        
        campaign = Campaign_information.get()
        
        response_names = list(input.checkbox())
        response_ids = {response_names[i] : [i] for i in range(len(response_names))}
        
        response_chosen = input.parity_plot_response()
        response = int(response_ids.get(response_chosen)[0])
    
        return parity_plot(campaign.optimizer, response_id=response)
    
    @render.plot
    @reactive.event(input.param_matrix_decision)
    def parameter_interaction_matrix():
       
        #Read in the user choice of whether or not they want a surface plot
        choice = input.param_matrix_decision()
        results = next_suggest.get()
        campaign = Campaign_information.get()

        if choice == True:

            if results is None or results.empty:
                return "No information available - please check your case for errors"
            
            response_names = list(input.checkbox())
            print(results)
            test_corr = results.corr()
            print(test_corr)
            
            return  obs_plot_interact(campaign.optimizer, test_corr) 
        else: 
            return None
        
    @render.ui
    @reactive.event(input.param_matrix_decision)
    def download_param_button():
        choice = input.param_matrix_decision()

        if choice == True: 
            return ui.download_button("download_param_matrix", "Download Produced Plot")
        else: 
            return None
        
    @render.download(filename="Parameter_Matrix.png")
    def download_param_matrix():
        results = next_suggest.get()
        campaign = Campaign_information.get()

        response_names = list(input.checkbox())
        test_corr = results.corr()
        fig = obs_plot_interact(campaign.optimizer, test_corr)
        with io.BytesIO() as buf:
            fig.savefig(buf, format="png", bbox_inches='tight')
            yield buf.getvalue()
        

    @render.download(filename="Results.xlsx")
    def results_download():
        
        config_data = input.selected_config()
        results = next_suggest.get()
        results = results.round(2)

        if results.empty:
            return None 
        else:
            if config_data == "No_data":

                #file_name = "Initial_Sampling.xlsx"

                with io.BytesIO() as buf:
                    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                        results.to_excel(writer, index=False)
                        # Ensure everything is written
                        writer.close()  
                
                    buf.seek(0)  # Go back to the beginning of the buffer
                    yield buf.getvalue()
            
            elif config_data == "Model_training":
                
                #file_name = "Bayesian_Optimisation.xlsx"

                with io.BytesIO() as buf:
                    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
                        results.to_excel(writer, index=False)
                        # Ensure everything is written
                        writer.close()  
                
                    buf.seek(0)  # Go back to the beginning of the buffer
                    yield buf.getvalue()
    

###################################################################################################
############ Submit Feedback Code - for internal apps only, otherwise delete this section #########
    email_string = reactive.value(None)
    
    @output
    @render.ui
    def submit_feedback_ui_id():
        return ui.a(
        ui.input_action_button(id = "submit_feedback_id", label ="Submit Feedback", icon=icon_svg("envelope"), width ="100%", class_ = "Green-Button", style="margin-top: 125px;"),
        href=email_string()
        )
    
    @reactive.effect
    def _():
         req(input.feedback_type_id() and input.feedback_webapp_name_id() and input.feedback_details_id())
         
         feedback_type = input.feedback_type_id().replace(" ", "%20")
         WebApp_name = input.feedback_webapp_name_id().replace(" ", "%20")
         feedback_details = input.feedback_details_id().replace(" ", "%20")
         
         email_string_temp = "mailto:shinyapps@approcess.com" + "?subject=" + feedback_type + ":%20%20" + WebApp_name + "&body=" + feedback_details
         email_string.set(email_string_temp)
         
         
    @output
    @render.text
    def copyright_company_URL_id():
         return ui.div(ui.HTML("&#169"),ui.span(datetime.now().year),ui.span(" "), ui.a("APC", href = "https://approcess.com/")) 

    @output
    @render.text
    def Version_track_id():
          return Web_app_version
###########################################################################

#################### Run App (do not edit) ################################
#app = App(app_ui,server, static_assets={"/www":resource_dir})
#app = App(app_ui,server)

www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets = www_dir)

app.run(launch_browser = True)