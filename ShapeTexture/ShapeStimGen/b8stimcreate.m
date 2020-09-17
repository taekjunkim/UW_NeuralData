%%%%%%%%%%
%%%%%this is the stimulus creation program for the b8 stimuli
%%%%%51 stimuli in all. These were presented at 1, 2, 4 or 8 rotations
%%%%%based on rotational symmetry
%%%%%to create the stimuli, in addition to this program you need:
%%%%%vertices1.txt
%%%%%fvmax.m
%%%%%At the matlab prompt type the name of this program. When prompted for
%%%%%the stimulus number, type a number between 1 and 51.


fidr = fopen('vertices1.txt', 'r');
idx = 0;
j = input('Enter Stimulus number (1:51): ');
for i = 1:51
  vrtnum = fscanf(fidr, '%d', [1, 1]);
  disp(vrtnum);
  in = (fscanf(fidr, '%f', [2, vrtnum]))';
  if(j == i)
    figure;
    bufvert = fvmax(in);
    subplot(2,2,1); 
    fill([-2.0 2.0 2.0 -2.0], [-2.0 -2.0 2.0 2.0], 'k', 'EdgeColor', 'none');
    hold
    fill(bufvert(:,1), bufvert(:,2), 'w');
    
  end
end
fclose(fidr);
