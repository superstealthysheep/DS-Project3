#!/usr/bin/env bash

kubectl.exe delete -f "k8s/storage-service.yaml"
kubectl.exe delete -f "k8s/storage-statefulset.yaml"
kubectl.exe delete -f "k8s/frontend-deployment.yaml"
kubectl.exe delete -f "k8s/frontend-service.yaml"
