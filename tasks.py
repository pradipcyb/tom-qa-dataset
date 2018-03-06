import numpy as np


from clause import Clause, Question
from oracle import Oracle
from actions import *
from collections import defaultdict


class Task(object):

    def __init__(self,
                 num_questions=5,
                 exit_prob=1.,
                 informant_prob=1.,
                 search_prob=1.,
                 test_cond='first order'):

        self.num_questions = num_questions

        self.search_prob = search_prob

        self.exit_inform_probs = [1 - exit_prob,
                                  exit_prob * (1 - informant_prob),
                                  exit_prob * informant_prob]
        assert sum(self.exit_inform_probs) == 1

        assert test_cond in ['first order',
                             'second order',
                             'reality',
                             'memory'], \
            "Invalid test condition: %s" % test_cond
        self.test_cond = test_cond

    def generate_story(self, world):
        raise NotImplementedError("Abstract method.")

class SimBeliefsTask(Task):
    def generate_story(self, world, length=25, num_agents=2, num_locations=1, num_objects=1):
        """
        Returns a list of clauses in story
        """

        idx_support_dummy = [0]
        actors = world.get_actors()
        locations = world.get_locations()
        objects = world.get_objects()
        containers = world.get_containers()
        
        random_actors = np.random.choice(actors, size=num_agents, replace=False)
        random_locations = np.random.choice(locations, size=num_locations, replace=False)
        random_objects = np.random.choice(objects, size=num_objects, replace=False)
        random_containers = np.random.choice(containers, size=num_locations*2, replace=False)
        
        oracle = Oracle(random_actors, random_locations, random_objects)
        
        # Populate locations in the oracle with containers
        locations = oracle.locations
        for i in range(len(random_locations)):
            location = random_locations[i]
            objects = random_obects[2i:2i+2] # TODO: find better way to assign containers
            locations.set_containers(location, objects)
        
        # Generate elements used to build stories
        # TODO: change from simple true belief story
        Clause([1, 2], LocationAction(), random_actors[0], random_actors[1], random_location)
        Question(idx_support_dummy, SearchedAction(), random_actors[1], random_object, random_containers[1])
                        
        return story
        
class TFTFBeliefsTask(Task):
    """
    For each triplet in a set of triplets
    randomly selected from world, generates 12
    stories: a true belief, false belief, and second
    order false belief story each with one of 4
    questions.
    
    Returns dictionary
    """
    def generate_story(self, world):

        idx_support_dummy = [0]
        actors = world.get_actors()
        locations = world.get_locations()
        objects = world.get_objects()
        containers = world.get_containers()
        
        random_actors = np.random.choice(actors, size=3, replace=False)
        random_location = np.random.choice(locations)
        random_object = np.random.choice(objects)
        random_containers = np.random.choice(containers, size=2, replace=False)    
        stories = defaultdict(list) # each entry will hold list of lists of clauses
        
        # Generate elements used to build stories
        clauses = [Clause([1, 2], LocationAction(), random_actors[0],
                          random_actors[1], random_location),
                   Clause([1, 2], ObjectLocAction(), random_object,
                          random_containers[0]),
                   Clause([1, 2], ExitedAction(), random_actors[1],
                          random_location),
                   Clause([1, 3], MoveAction(), random_actors[0],
                          random_object, random_containers[1]),
                   Clause([2, 3], TellAction(), random_actors[2],
                          random_actors[1], random_object),
                   Clause([1, 2], EnterAction(), random_actors[1],
                          random_location)] # TODO: improve naming
            
        # assumes no support clause    
        
        stories['TrueBelief'].append([clauses[0], clauses[1], clauses[3],
                                      Question(idx_support_dummy, SearchedAction(),
                                               random_actors[1], random_object,
                                               random_containers[1]
                                              )])
            
        stories['FalseBelief'].append(clauses[0:4] + [clauses[-1]] +
                                      [Question(idx_support_dummy, SearchedAction(),
                                                random_actors[1], random_object,
                                                random_containers[0]
                                               )])
            
        stories['SecondOrderFalseBelief'].append(clauses +
                                                 [Question(idx_support_dummy, SearchedAction(),
                                                           random_actors[1],
                                                           random_object,
                                                           random_containers[1]
                                                          )])
 
        stories['TrueBelief'].append([clauses[0], clauses[1], clauses[3],
                                      Question(idx_support_dummy, BeliefSearchAction(),
                                               random_actors[0], random_actors[1],
                                               random_object, random_containers[1]
                                              )])

        stories['FalseBelief'].append(clauses[0:4] + [clauses[-1]] +
                                      [Question(idx_support_dummy, BeliefSearchAction(),
                                               random_actors[0], random_actors[1],
                                               random_object, random_containers[0]
                                              )])
            
        stories['SecondOrderFalseBelief'].append(clauses +
                                     [Question(idx_support_dummy, BeliefSearchAction(),
                                               random_actors[0], random_actors[1],
                                               random_object, random_containers[0]
                                              )])
        
        stories['TrueBelief'].append([clauses[0], clauses[1], clauses[3],
                                      Question(idx_support_dummy, RealityAction(),
                                               random_object, random_containers[1]
                                              )])

        stories['FalseBelief'].append(clauses[0:4] + [clauses[-1]] +
                                      [Question(idx_support_dummy, RealityAction(),
                                               random_object, random_containers[1]
                                              )])
            
        stories['SecondOrderFalseBelief'].append(clauses +
                                      [Question(idx_support_dummy, RealityAction(),
                                               random_object, random_containers[1]
                                              )])
        
        stories['TrueBelief'].append([clauses[0], clauses[1], clauses[3],
                                      Question(idx_support_dummy, MemoryAction(),
                                               random_object, random_containers[0]
                                              )])

        stories['FalseBelief'].append(clauses[0:4] + [clauses[-1]] +
                                      [Question(idx_support_dummy, MemoryAction(),
                                               random_object, random_containers[0]
                                              )])
            
        stories['SecondOrderFalseBelief'].append(clauses +
                                      [Question(idx_support_dummy, MemoryAction(),
                                               random_object, random_containers[0]
                                              )])
                        
        return stories

class ActionsBeliefsTask(Task):

    def generate_story(self, world):

        story = []

        actors = world.get_actors()
        locations = world.get_locations()
        objects = world.get_objects()
        containers = world.get_containers()

        num_questions = 0

        while num_questions < self.num_questions:

            idx_support = []
            clauses = []

            random_actors = np.random.choice(actors, size=3, replace=False)
            random_location = np.random.choice(locations)
            random_object = np.random.choice(objects)

            # Whether or not the person will maintain a false belief
            exit_enter = np.random.choice([0, 1, 2], p=self.exit_inform_probs)

            # Whether to include the search clause
            do_search = np.random.choice([True, False],
                                         p=[self.search_prob,
                                            1 - self.search_prob])

            if do_search:
                random_containers = np.random.choice(containers,
                                                     size=3,
                                                     replace=False)
            else:
                random_containers = np.random.choice(containers,
                                                     size=2,
                                                     replace=False)

            if do_search:

                # Person A searches for the item somewhere
                clauses.append(
                    Clause(
                        [1, 2],
                        SearchAction(),
                        random_actors[0],
                        random_object,
                        random_containers[2],
                    )
                )

            clauses.append(
                Clause(
                    [1, 2],
                    PlaceAction(),
                    random_actors[0],
                    random_object,
                    random_containers[0],
                )
            )

            if exit_enter == 1 or exit_enter == 2:

                # Support is "placed" clause
                idx_support += [len(story) + len(clauses) - 1]

                # Person A exits the location
                clauses.append(
                    Clause(
                        [1, 2],
                        ExitAction(),
                        random_actors[0],
                        random_location,
                    )
                )

            else:

                # Support is "moved" clause
                idx_support += [len(story) + len(clauses)]

            # Person B moves the item from container X to container Y
            clauses.append(
                Clause(
                    [1] if exit_enter == 1 or exit_enter == 2 else [1, 2],
                    TransportAction(),
                    random_actors[1],
                    random_object,
                    random_containers[0],
                    random_containers[1],
                )
            )

            if exit_enter == 2:

                # Person A is informed
                clauses.append(
                    Clause(
                        [2],
                        InformLocationAction(),
                        random_actors[2],
                        random_actors[0],
                        random_object,
                        random_containers[1]
                    )
                )

            if exit_enter == 1 or exit_enter == 2:

                # Person A re-enters the location
                clauses.append(
                    Clause(
                        [1, 2],
                        EnterAction(),
                        random_actors[0],
                        random_location,
                    )
                )

            story.extend(clauses)

            if self.test_cond == 'first order':

                believe_loc = random_containers[0] \
                    if exit_enter == 1  \
                    else random_containers[1]

                # Question: Where does person A believe is the item?
                story.append(
                    Question(
                        idx_support,
                        BelieveLocationAction(),
                        random_actors[0],
                        random_object,
                        believe_loc,
                    )
                )

            elif self.test_cond == 'second order':

                believe_loc = random_containers[1] \
                    if exit_enter == 0 \
                    else random_containers[0]

                # Question: Where does person B think A believes the item is?
                story.append(
                    Question(
                        idx_support,
                        BelieveAgentBelieveLocationAction(),
                        random_actors[1],
                        random_actors[0],
                        random_object,
                        believe_loc,
                    )
                )

            elif self.test_cond == 'reality':

                loc = random_containers[1]

                # Question: Where is the item in reality?
                story.append(
                    Question(
                        idx_support,
                        Exist(),
                        random_object,
                        loc,
                    )
                )

            elif self.test_cond == 'memory':

                loc = random_containers[0]

                # Question: Where was the item at the beginning of the story?
                story.append(
                    Question(
                        idx_support,
                        ExistBeginning(),
                        random_object,
                        loc,
                    )
                )

            else:
                raise NotImplementedError

            num_questions += 1

        return story


class BeliefsActionsTask(Task):

    def generate_story(self, world):

        story = []

        actors = world.get_actors()
        locations = world.get_locations()
        objects = world.get_objects()
        containers = world.get_containers()

        num_questions = 0

        while num_questions < self.num_questions:

            idx_support = []
            clauses = []

            random_actors = np.random.choice(actors, size=3, replace=False)
            random_location = np.random.choice(locations)
            random_object = np.random.choice(objects)
            random_containers = np.random.choice(containers,
                                                 size=2,
                                                 replace=False)

            # whether or not the person will maintain a false belief
            exit_enter = np.random.choice([0, 1, 2], p=self.exit_inform_probs)

            if exit_enter == 1 or exit_enter == 2:

                # Person A believes a false state of affairs
                clauses.append(
                    Clause(
                        [2],
                        BelieveLocationAction(),
                        random_actors[0],
                        random_object,
                        random_containers[0]
                    )
                )

                # Support is false "belief" clause
                idx_support += [len(story) + len(clauses) - 1]

                # Person A exits the location
                clauses.append(
                    Clause(
                        [1, 2],
                        ExitAction(),
                        random_actors[0],
                        random_location
                    )
                )

            # Person B moves the item from container X to container Y
            clauses.append(
                Clause(
                    [1] if exit_enter in [1, 2] else [1, 2],
                    TransportAction(),
                    random_actors[1],
                    random_object,
                    random_containers[0],
                    random_containers[1]
                )
            )

            if exit_enter == 2:

                # Person A is informed
                clauses.append(
                    Clause(
                        [2],
                        InformLocationAction(),
                        random_actors[2],
                        random_actors[0],
                        random_object,
                        random_containers[1]
                    )
                )

            if exit_enter == 1 or exit_enter == 2:

                # Person A re-enters the location
                clauses.append(
                    Clause(
                        [1, 2],
                        EnterAction(),
                        random_actors[0],
                        random_location
                    )
                )

            else:

                # Person A believes a true state of affairs
                clauses.append(
                    Clause(
                        [2],
                        BelieveLocationAction(),
                        random_actors[0],
                        random_object,
                        random_containers[1]
                    )
                )

                # Support is true "belief" clause
                idx_support += [len(story) + len(clauses) - 1]

            story.extend(clauses)

            # Clause: where does person A seach for the item?
            if self.test_cond == 'first order':

                believe_loc = random_containers[0] \
                    if exit_enter == 1 \
                    else random_containers[1]

                # Question: Where does person A search for the item?
                story.append(
                    Question(
                        idx_support,
                        SearchAction(),
                        random_actors[0],
                        random_object,
                        believe_loc,
                    )
                )

            elif self.test_cond == 'second order':

                believe_loc = random_containers[1] \
                    if exit_enter == 0 \
                    else random_containers[0]

                # Question: Where does person B think A will search?
                story.append(
                    Question(
                        idx_support,
                        BelieveAgentSearchLocationAction(),
                        random_actors[1],
                        random_actors[0],
                        random_object,
                        believe_loc,
                    )
                )

            elif self.test_cond == 'reality':

                loc = random_containers[1]

                # Question: Where is the item in reality?
                story.append(
                    Question(
                        idx_support,
                        Exist(),
                        random_object,
                        loc,
                    )
                )

            elif self.test_cond == 'memory':

                loc = random_containers[0]

                # Question: Where was the item at the beginning of the story?
                story.append(
                    Question(
                        idx_support,
                        ExistBeginning(),
                        random_object,
                        loc,
                    )
                )

            else:
                raise NotImplementedError

            num_questions += 1

        return story


class ActionsBeliefsActionsTask(Task):

    def generate_story(self, world):

        story = []

        actors = world.get_actors()
        locations = world.get_locations()
        objects = world.get_objects()
        containers = world.get_containers()

        num_questions = 0

        while num_questions < self.num_questions:

            idx_support = []
            clauses = []

            random_actors = np.random.choice(actors, size=3, replace=False)
            random_location = np.random.choice(locations)
            random_object = np.random.choice(objects)
            random_containers = np.random.choice(containers, size=2,
                                                 replace=False)

            # Whether or not the person will maintain a false belief
            exit_enter = np.random.choice([0, 1, 2], p=self.exit_inform_probs)

            # Person A drops the item in container X
            clauses.append(
                Clause(
                    [1, 2],
                    PlaceAction(),
                    random_actors[0],
                    random_object,
                    random_containers[0]
                )
            )

            if exit_enter in [1, 2]:

                # Support is "placed" clause
                idx_support += [len(story) + len(clauses) - 1]

                # person A exits the location
                clauses.append(
                    Clause(
                        [1, 2],
                        ExitAction(),
                        random_actors[0],
                        random_location
                    )
                )

            # Person B moves the item from container X to container Y
            clauses.append(
                Clause(
                    [1] if exit_enter in [1, 2] else [1, 2],
                    TransportAction(),
                    random_actors[1],
                    random_object,
                    random_containers[0],
                    random_containers[1]
                )
            )

            if exit_enter == 2:

                # Person A is informed
                clauses.append(
                    Clause(
                        [2],
                        InformLocationAction(),
                        random_actors[2],
                        random_actors[0],
                        random_object,
                        random_containers[1]
                    )
                )

            if exit_enter in [1, 2]:

                # Person A re-enters the location
                clauses.append(
                    Clause(
                        [1, 2],
                        EnterAction(),
                        random_actors[0],
                        random_location
                    )
                )

            else:

                # Support is "transported" clause
                idx_support += [len(story) + len(clauses) - 1]

            story.extend(clauses)

            # Question
            if self.test_cond == 'first order':

                believe_loc = random_containers[0] \
                    if exit_enter == 1 \
                    else random_containers[1]

                # Question: Where does person A search for the item?
                story.append(
                    Question(
                        idx_support,
                        SearchAction(),
                        random_actors[0],
                        random_object,
                        believe_loc,
                    )
                )

            elif self.test_cond == 'second order':

                believe_loc = random_containers[1] \
                    if exit_enter == 0 \
                    else random_containers[0]

                # Question: Where does person B think A believes the item is?
                story.append(
                    Question(
                        idx_support,
                        BelieveAgentSearchLocationAction(),
                        random_actors[1],
                        random_actors[0],
                        random_object,
                        believe_loc,
                    )
                )

            elif self.test_cond == 'reality':

                loc = random_containers[1]

                # Question: Where is the item in reality?
                story.append(
                    Question(
                        idx_support,
                        Exist(),
                        random_object,
                        loc,
                    )
                )

            elif self.test_cond == 'memory':

                loc = random_containers[0]

                # Question: Where was the item at the beginning of the story?
                story.append(
                    Question(
                        idx_support,
                        ExistBeginning(),
                        random_object,
                        loc,
                    )
                )

            else:
                raise NotImplementedError

            num_questions += 1

        return story
