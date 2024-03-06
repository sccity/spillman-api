FROM nginx:alpine
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:80/ || exit 1
CMD ["nginx", "-g", "daemon off;"]