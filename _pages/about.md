---
layout: about
title: About
permalink: /
subtitle: >
  Ph.D. Candidate, <a href='https://engineering.uga.edu/schools/ecam/'>School of Environmental, Civil, Agricultural and Mechanical Engineering</a>,
  <a href='https://engineering.uga.edu/'>College of Engineering</a>,
  <a href='https://www.uga.edu/'>University of Georgia</a> ·
  <a href='https://sites.google.com/view/xin-zhang-lab/home'>SAAS Lab</a>

profile:
  align: right
  image: prof_pic.jpg
  image_circular: false # crops the image to make it circular
  more_info: >
    <p>Riverbend Research Lab North, 001E</p>
    <p>110 Riverbend Rd, Athens, GA 30605</p>
    <p><a href="mailto:theva@uga.edu">theva@uga.edu</a></p>

selected_papers: true # includes a list of papers marked as "selected={true}"
social: true # includes social icons at the bottom of the page

announcements:
  enabled: true # includes a list of news items
  scrollable: true # adds a vertical scroll bar if there are more than 3 news items
  limit: 7 # leave blank to include all the news in the `_news` folder

latest_posts:
  enabled: true
  scrollable: true # adds a vertical scroll bar if there are more than 3 new posts items
  limit: 3 # leave blank to include all the blog posts
---

I build **robots that can see well enough to harvest**. I am a Ph.D. candidate in Agricultural Engineering at the University of Georgia, working with **Dr. [Xin Zhang](https://sites.google.com/view/xin-zhang-lab/home)** in the Sensing and Automation in Agri-Systems (SAAS) Lab, where I develop vision-guided autonomous systems for specialty-crop harvesting and food processing — from simulation through field deployment.

**I am currently searching for new positions.** My [CV]({{ '/cv/' | relative_url }}) is available here, and I am happy to discuss opportunities in agricultural robotics, computer vision, and autonomous field systems.

#### Research

- **Autonomous selective harvesting.** I designed and open-sourced [CottonSim](https://github.com/imtheva/CottonSim), a ROS/Gazebo simulator and vision-guided navigation stack for a lightweight robotic cotton picker built on a Clearpath Husky. The perception module reached 85.2% mAP, and the system completed autonomous field traversal at a 100% rate under GPS guidance and 96.7% under map-based guidance.
- **Perception for delicate produce.** I built a multi-ripeness blackberry detection pipeline for soft robotic harvesting, benchmarking nine YOLO architectures across a two-season, 1,086-image field dataset acquired in commercial orchards.
- **Manipulation.** I develop boll orientation-aware manipulator control for a UR5e with dual-side harvesting capability, using stereo perception to plan approaches around occluded and awkwardly oriented targets.
- **Food-processing automation.** With the USDA-ARS, I applied semantic segmentation to automate the catfish cutting process, reaching 89.2% mIoU with SegFormer-B5.

Previously I was a Graduate Research Assistant in the Department of Agricultural and Biological Engineering at Mississippi State University, and before that Lecturer (Probationary) at Uva Wellassa University in Sri Lanka, where I was instructor of record for eight undergraduate courses in electronics, embedded systems, and intelligent systems.

Please [get in touch](mailto:theva@uga.edu) if you would like to talk about agricultural robotics, field perception, or collaboration.
