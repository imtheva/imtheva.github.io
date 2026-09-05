// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "About",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "Publications",
          description: "Publications including journal articles, conference papers, and book chapters, organized by category in reverse chronological order.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-blog",
          title: "Blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "nav-projects",
          title: "Projects",
          description: "A collection of past and current research and projects.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-curriculum-vitae",
          title: "Curriculum Vitae",
          description: "Download the full CV as a PDF using the icon above. Last updated September 2026.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "dropdown-news",
              title: "News",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/news/";
              },
            },{id: "dropdown-teaching",
              title: "Teaching",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/teaching/";
              },
            },{id: "dropdown-repositories",
              title: "Repositories",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/repositories/";
              },
            },{id: "dropdown-gallery",
              title: "Gallery",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/gallery/";
              },
            },{id: "post-winter-storms-how-they-form-why-they-re-dangerous-and-what-they-mean-for-agriculture",
        
          title: 'Winter Storms: How They Form, Why They’re Dangerous, and What They Mean for... <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "An overview of winter storms—how they form, how they differ from normal snow events, and the often-overlooked impacts they have on agriculture, livestock, and farming systems.",
        section: "Posts",
        handler: () => {
          
            window.open("https://medium.com/@theva1993/winter-storms-how-they-form-why-theyre-dangerous-and-what-they-mean-for-agriculture-51dcf6c0ed30", "_blank");
          
        },
      },{id: "post-how-computer-vision-is-transforming-agricultural-engineering",
        
          title: 'How Computer Vision Is Transforming Agricultural Engineering <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "An accessible overview of how computer vision is transforming agricultural engineering through crop detection, robotics, and intelligent farm automation.",
        section: "Posts",
        handler: () => {
          
            window.open("https://medium.com/@theva1993/computer-vision-in-agricultural-engineering-0513dc142326", "_blank");
          
        },
      },{id: "post-from-science-fiction-to-farmland-why-robotics-amp-ai-are-inevitable-in-agriculture",
        
          title: 'From Science Fiction to Farmland: Why Robotics &amp; AI Are Inevitable in Agriculture... <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "My first Medium article on why robotics &amp; AI are becoming inevitable in agriculture.",
        section: "Posts",
        handler: () => {
          
            window.open("https://medium.com/@theva1993/from-science-fiction-to-farmland-why-robotics-and-ai-are-inevitable-in-agriculture-97c18d9d9956", "_blank");
          
        },
      },{id: "post-mis",
        
          title: "MIS",
        
        description: "A cost-effective remote health monitoring solution designed to continuously assess non-critical patients while reducing hospital congestion—especially during emergencies such as the COVID-19 pandemic.",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2025/MSc/";
          
        },
      },{id: "post-just-a-moment",
        
          title: 'Just a moment... <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.open("https://www.academia.edu/29809896/Making_Threads_in_SolidWorks", "_blank");
          
        },
      },{id: "post-just-a-moment",
        
          title: 'Just a moment... <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.open("https://www.academia.edu/32184335/Measuring_Pen_A_digital_device_to_measure_distance", "_blank");
          
        },
      },{id: "post-google-gemini-updates-flash-1-5-gemma-2-and-project-astra",
        
          title: 'Google Gemini updates: Flash 1.5, Gemma 2 and Project Astra <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "We’re sharing updates across our Gemini family of models and a glimpse of Project Astra, our vision for the future of AI assistants.",
        section: "Posts",
        handler: () => {
          
            window.open("https://blog.google/technology/ai/google-gemini-update-flash-ai-assistant-io-2024/", "_blank");
          
        },
      },{id: "post-displaying-external-posts-on-your-al-folio-blog",
        
          title: 'Displaying External Posts on Your al-folio Blog <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.open("https://medium.com/@al-folio/displaying-external-posts-on-your-al-folio-blog-b60a1d241a0a?source=rss-17feae71c3c4------2", "_blank");
          
        },
      },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the_godfather/";
            },},{id: "news-featured-featured-video-msu-graduate-school-recognition",
          title: '🎥 [Featured!] Featured Video: MSU Graduate School Recognition',
          description: "",
          section: "News",},{id: "news-award-msu-the-graduate-school-newsletter-awards-thevathayarajh-thayananthan",
          title: '🏆 [Award!] MSU The Graduate School Newsletter: Awards – Thevathayarajh Thayananthan',
          description: "",
          section: "News",},{id: "news-award-2023-sec-emerging-scholars",
          title: '🏆 [Award!] 2023 SEC Emerging Scholars .',
          description: "",
          section: "News",},{id: "news-featured-wcbi-mississippi-state-researchers-develop-prototype-to-advance-cotton-industry",
          title: '🎥 [Featured!] WCBI: Mississippi State researchers develop prototype to advance cotton industry',
          description: "",
          section: "News",},{id: "news-featured-msu-aai-market-day-report-talks-msu-s-agricultural-autonomy-institute",
          title: '🎥 [Featured!] MSU AAI: Market Day Report talks MSU’s Agricultural Autonomy Institute',
          description: "",
          section: "News",},{id: "news-award-msu-abe-newsletter-awards-thevathayarajh-thayananthan",
          title: '🏆 [Award!] MSU ABE Newsletter: Awards – Thevathayarajh Thayananthan .',
          description: "",
          section: "News",},{id: "news-featured-farm-flavor-agriculture-technology-advancements-revolutionize-mississippi-ag-industry",
          title: '🎥 [Featured!] Farm Flavor: Agriculture Technology Advancements Revolutionize Mississippi Ag Industry',
          description: "",
          section: "News",},{id: "news-new-paper-perception-enabled-manipulator-control-for-a-robotic-cotton-picker-with-dual-side-harvesting-capability",
          title: '📄 [New Paper!] Perception-enabled manipulator control for a robotic cotton picker with dual-side...',
          description: "",
          section: "News",},{id: "news-design-and-development-of-an-autonomous-vision-guided-cotton-picker-for-selective-and-targeted-robotic-picking-msu-otm",
          title: 'Design and development of an autonomous vision-guided cotton picker for selective and targeted...',
          description: "",
          section: "News",},{id: "news-new-paper-in-field-multi-ripeness-blackberry-detection-for-soft-robotic-harvesting",
          title: '📄 [New Paper!] In-Field Multi-Ripeness Blackberry Detection for Soft Robotic Harvesting',
          description: "",
          section: "News",},{id: "news-new-paper-cottonsim-a-vision-guided-autonomous-robotic-system-for-cotton-harvesting-in-gazebo-simulation",
          title: '📄 [New Paper!] CottonSim: A vision-guided autonomous robotic system for cotton harvesting in...',
          description: "",
          section: "News",},{id: "news-tech-tuesday-check-out-thevathayarajh-thayananthan-s-design-and-development-of-an-autonomous-vision-guided-cotton-picker-for-selective-and-targeted-robotic-picking-with-dr-xin-zhang",
          title: 'TECH TUESDAY: Check out Thevathayarajh Thayananthan’s Design and development of an autonomous vision-guided...',
          description: "",
          section: "News",},{id: "news-award-iipa-announces-2026-retreat-student-competition-winners-3rd-place-at-iipa-retreat-2026",
          title: '🏆 [Award!] IIPA Announces 2026 Retreat Student Competition- Winners ( 3rd Place at...',
          description: "",
          section: "News",},{id: "news-milestone-passed-my-comprehensive-examination-and-advanced-to-ph-d-candidacy-in-agricultural-engineering-at-the-university-of-georgia",
          title: '🎓 [Milestone!] Passed my comprehensive examination and advanced to Ph.D. candidacy in Agricultural...',
          description: "",
          section: "News",},{id: "projects-medical-instrumentation-system",
          title: 'Medical Instrumentation System',
          description: "A cost-effective remote health monitoring solution designed to continuously assess non-critical patients while reducing hospital congestion—especially during emergencies such as the COVID-19 pandemic.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},{id: "projects-cottonsim",
          title: 'CottonSim',
          description: "This study proposes a lightweight, small-scale, vision-guided autonomous robotic cotton picker as an alternative in a simulation environment.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_CottonSimulation/";
            },},{id: "projects-blackberry-detection",
          title: 'Blackberry Detection',
          description: "This study focuses on developing computer vision and deep learning models to identify and classify blackberries by their ripeness stages.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/3_Blackberry/";
            },},{
        id: 'social-blogger',
        title: 'Blogger',
        section: 'Socials',
        handler: () => {
          window.open("https://imtheva.github.io/blog/", "_blank");
        },
      },{
        id: 'social-cv',
        title: 'CV',
        section: 'Socials',
        handler: () => {
          window.open("/assets/pdf/Thayananthan_CV.pdf", "_blank");
        },
      },{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%74%68%65%76%61@%75%67%61.%65%64%75", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/imtheva", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/imtheva", "_blank");
        },
      },{
        id: 'social-medium',
        title: 'Medium',
        section: 'Socials',
        handler: () => {
          window.open("https://medium.com/@theva1993", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0009-0007-2576-4348", "_blank");
        },
      },{
        id: 'social-researchgate',
        title: 'ResearchGate',
        section: 'Socials',
        handler: () => {
          window.open("https://www.researchgate.net/profile/Thevathayarajh-Thayananthan/", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=MpKhKEUAAAAJ", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
