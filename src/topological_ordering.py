def top_order(subjects):
    ordered_subjects = []
    count_vector = []

    for subj in subjects:
        count_vector.append(len(subj.prereqs))
    
    for subj in subjects:
        #print(count_vector) #debug
        if 0 in count_vector:
            i = count_vector.index(0)
            count_vector[i] = count_vector[i]-1
            ordered_subjects.append(subjects[i])
                
            for j in range(0, len(subjects)):
                if subjects[i].name in subjects[j].prereqs:
                    count_vector[j] = count_vector[j]-1
        else:
            return []
            
    return ordered_subjects
        