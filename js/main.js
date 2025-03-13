// Initialize AOS (Animate On Scroll)
AOS.init({
  duration: 800,
  once: true,
  offset: 100,
})

// Navbar scroll effect
window.addEventListener('scroll', function () {
  if (window.scrollY > 50) {
    document.getElementById('navbar').classList.add('scrolled')
  } else {
    document.getElementById('navbar').classList.remove('scrolled')
  }
})

// Optional: Parallax effect for header
window.addEventListener('scroll', function () {
  const scrolled = window.pageYOffset
  const header = document.querySelector('header')
  if (header) {
    header.style.transform = `translateY(${scrolled * 0.5}px)`
  }
})

// Add active state to navigation links based on scroll position
window.addEventListener('scroll', function () {
  const sections = document.querySelectorAll('section')
  const navLinks = document.querySelectorAll('.nav-links a')

  let current = ''

  sections.forEach((section) => {
    const sectionTop = section.offsetTop
    const sectionHeight = section.clientHeight
    if (pageYOffset >= sectionTop - 200) {
      current = section.getAttribute('id')
    }
  })

  navLinks.forEach((link) => {
    link.classList.remove('active')
    if (link.getAttribute('href').slice(1) === current) {
      link.classList.add('active')
    }
  })
})

// Fade effect for header and profile image
window.addEventListener('scroll', function () {
  const header = document.querySelector('header')
  const profileImage = document.querySelector('.profile-image-container')
  const headerContent = document.querySelector('.header-content')
  const researchSection = document.querySelector('#research')

  if (researchSection) {
    const researchPosition = researchSection.getBoundingClientRect().top
    const windowHeight = window.innerHeight

    if (researchPosition < windowHeight) {
      const opacity = Math.max(0, Math.min(1, researchPosition / windowHeight))
      headerContent.style.opacity = opacity
      profileImage.style.opacity = opacity
      headerContent.style.transform = `translateY(${(1 - opacity) * -50}px)`
      profileImage.style.transform = `translateY(${(1 - opacity) * -50}px)`
    } else {
      headerContent.style.opacity = 1
      profileImage.style.opacity = 1
      headerContent.style.transform = 'translateY(0)'
      profileImage.style.transform = 'translateY(0)'
    }
  }
})

// Scholar stats and publications functions
async function updateScholarStats() {
  try {
    const response = await fetch('./assets/data/scholar_stats.json')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    document.getElementById('citation-count').textContent = data.citations
    document.getElementById('publication-count').textContent = data.publications
    document.getElementById('h-index').textContent = data.h_index
    document.getElementById('last-updated').textContent = data.last_updated
  } catch (error) {
    console.error('Error fetching scholar stats:', error)
  }
}

async function updatePublications() {
  try {
    const response = await fetch('./assets/data/scholar_stats.json')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    const publicationList = document.getElementById('recent-publications')

    if (!publicationList) {
      console.error('Publication list container not found!')
      return
    }

    publicationList.innerHTML = ''

    if (data.recent_publications && data.recent_publications.length > 0) {
      // Use slice to get the first three publications
      const recentPublications = data.recent_publications.slice(0, 3)

      recentPublications.forEach((pub, index) => {
        const pubDiv = document.createElement('div')
        pubDiv.className = 'publication-item'
        pubDiv.setAttribute('data-aos', 'fade-up')

        pubDiv.innerHTML = `
                    <div class="publication-year">${pub.year}</div>
                    <h3><a href="${pub.url}" target="_blank">${
          pub.title
        }</a></h3>
                    <p class="Journal">${
                      pub.citation || 'Citation not available'
                    }</p>
                    <button class="abstract-toggle" onclick="toggleAbstract(${index})">
                        Show Abstract
                    </button>
                    <div class="abstract" id="abstract-${index}" style="display: none;">
                        ${pub.abstract || 'Abstract not available'}
                    </div>
                `

        publicationList.appendChild(pubDiv)
      })
    }
  } catch (error) {
    console.error('Error updating publications:', error)
  }
}

async function updatePublications_all() {
  try {
    const response = await fetch('./assets/data/scholar_stats.json')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    const publicationList = document.getElementById('all-publications') // Change to 'all-publications'

    if (!publicationList) {
      console.error('Publication list container not found!')
      return
    }

    publicationList.innerHTML = '' // Clear previous content

    if (data.recent_publications && data.recent_publications.length > 0) {
      // Remove the slice method to display all publications
      data.recent_publications.forEach((pub, index) => {
        const pubDiv = document.createElement('div')
        pubDiv.className = 'publication-item'
        pubDiv.setAttribute('data-aos', 'fade-up')

        pubDiv.innerHTML = `
                    <div class="publication-year">${pub.year}</div>
                    <h3><a href="${pub.url}" target="_blank">${
          pub.title
        }</a></h3>
                    <p class="Journal">${
                      pub.citation || 'Citation not available'
                    }</p>
                    <button class="abstract-toggle" onclick="toggleAbstract(${index})">
                        Show Abstract
                    </button>
                    <div class="abstract" id="abstract-${index}" style="display: none;">
                        ${pub.abstract || 'Abstract not available'}
                    </div>
                `

        publicationList.appendChild(pubDiv) // Append the new publication item
      })
    }
  } catch (error) {
    console.error('Error updating publications:', error)
  }
}

function toggleAbstract(index) {
  const abstractDiv = document.getElementById(`abstract-${index}`)
  const button = abstractDiv.previousElementSibling

  if (abstractDiv.style.display === 'none') {
    abstractDiv.style.display = 'block'
    button.textContent = 'Hide Abstract'
  } else {
    abstractDiv.style.display = 'none'
    button.textContent = 'Show Abstract'
  }
}

// Single DOMContentLoaded event listener for all initializations
document.addEventListener('DOMContentLoaded', function () {
  // Mobile menu functionality
  const hamburger = document.querySelector('.hamburger')
  const navLinks = document.querySelector('.nav-links')
  const navLinksItems = document.querySelectorAll('.nav-links a')

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function (e) {
      e.stopPropagation()
      hamburger.classList.toggle('active')
      navLinks.classList.toggle('active')
    })

    navLinksItems.forEach((item) => {
      item.addEventListener('click', function () {
        hamburger.classList.remove('active')
        navLinks.classList.remove('active')
      })
    })
  }

  // Close menu when clicking outside
  document.addEventListener('click', function (e) {
    if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
      hamburger.classList.remove('active')
      navLinks.classList.remove('active')
    }
  })

  // Smooth scrolling
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault()
      const target = document.querySelector(this.getAttribute('href'))
      if (target) {
        const headerOffset = 100
        const elementPosition = target.getBoundingClientRect().top
        const offsetPosition =
          elementPosition + window.pageYOffset - headerOffset

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth',
        })
      }
    })
  })

  // Update scholar stats and publications
  updateScholarStats()
  updatePublications()
})

// Optional: Add loading animation
window.addEventListener('load', function () {
  document.body.classList.add('loaded')
})

// Function to update the footer year and last updated date
function updateFooterDate() {
  const currentYear = new Date().getFullYear()
  document.getElementById('year').textContent = currentYear

  // Set a fixed "last updated" date (replace this with the date you pushed your changes)
  const lastUpdatedDate = new Date('2025-03-13').toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  document.getElementById('footer-last-updated').textContent = lastUpdatedDate
}

// Run the function when the page loads
document.addEventListener('DOMContentLoaded', updateFooterDate)

// JavaScript for carousel functionality
let currentIndex = 0
const images = document.querySelectorAll('.carousel-images img')
const dots = document.querySelectorAll('.carousel-dots .dot')

// Function to change the image
function changeImage() {
  // Move the images by the current index
  const carouselImages = document.querySelector('.carousel-images')
  carouselImages.style.transform = `translateX(-${currentIndex * 100}%)`

  // Update active dot
  dots.forEach((dot) => dot.classList.remove('active'))
  dots[currentIndex].classList.add('active')
}

// Function to move to the next image
function nextImage() {
  currentIndex = (currentIndex + 1) % images.length
  changeImage()
}

// Function to move to the previous image
function prevImage() {
  currentIndex = (currentIndex - 1 + images.length) % images.length
  changeImage()
}

// Auto slide images every 3 seconds
setInterval(nextImage, 3000)

// Click on dot to navigate to that image
dots.forEach((dot, index) => {
  dot.addEventListener('click', () => {
    currentIndex = index
    changeImage()
  })
})

// Initial call to set the first image
changeImage()
