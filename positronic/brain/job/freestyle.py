# -*- coding: utf-8 -*-
#
# Positronic Brain - Opinionated Buildbot Workflow
# Copyright (C) 2014  Develer S.r.L.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from functools import partial
from random import randrange

from buildbot.changes.filter import ChangeFilter
from buildbot.process.properties import Interpolate
from buildbot.changes.svnpoller import SVNPoller
from buildbot.schedulers.basic import SingleBranchScheduler
from buildbot.schedulers.triggerable import Triggerable
from buildbot.status.mail import MailNotifier
from buildbot.steps.shell import ShellCommand
from buildbot.steps.source.svn import SVN

from positronic.brain.artifact import add_artifact_pre_build_steps, add_artifact_post_build_steps
from positronic.brain.config import BrainConfig, BuildmasterConfig
from positronic.brain.job import Job
from positronic.brain.mail import html_message_formatter
from positronic.brain.utils import has_svn_change_source, hashify, scheduler_name, is_dir_in_change


class FreestyleJob(Job):
    def __init__(self, name, workers):
        super(FreestyleJob, self).__init__(name, workers)

        add_artifact_pre_build_steps(self)

        # Add a "triggerable" build step so that other jobs can trigger us.
        BuildmasterConfig['schedulers'].append(Triggerable(
            name=scheduler_name(self, 'trigger'),
            builderNames=[self.name]))

    def __exit__(self, type, value, traceback):
        # As the last step, we grab artifacts from the worker. This MUST always be the last step.
        add_artifact_post_build_steps(self)

    def checkout(self, workdir, url, branch):
        repo_url = '%s/%s' % (url, branch)

        self.add_step(SVN(
            mode='full',
            method='clean',
            repourl=repo_url,
            workdir=workdir))

    def command(self, *args, **kwargs):
        env = {
            'BUILD': Interpolate('%(prop:buildnumber)s'),
            'BUILD_ARTIFACTS': Interpolate('%(prop:artifactsdir)s'),
            'CI': '1',
        }

        if 'env' in kwargs:
            kwargs['env'].update(env)
        else:
            kwargs['env'] = env

        self.add_step(ShellCommand(command=list(args), **kwargs))

    def notify(self, *recipients):
        BuildmasterConfig['status'].append(MailNotifier(
            builders=[self.name],
            extraRecipients=recipients,
            fromaddr=BrainConfig['emailFrom'],
            messageFormatter=html_message_formatter,
            mode=['change', 'failing'],
            sendToInterestedUsers=False))

    def watch(self, url, branch):
        repo_url = '%s/%s' % (url, branch)

        if not has_svn_change_source(repo_url):
            BuildmasterConfig['change_source'].append(SVNPoller(
                svnurl=repo_url,
                pollInterval=300 + randrange(0, 60),
                histmax=5))

        BuildmasterConfig['schedulers'].append(SingleBranchScheduler(
            name=scheduler_name(self, 'svn-' + hashify(repo_url)),
            treeStableTimer=60,
            builderNames=[self.name],
            change_filter=ChangeFilter(repository=repo_url)))

    def watch_paths(self, paths):
        """
        Start the build if an incoming change-set contains files that begin with the given
        directory names.

        """
        BuildmasterConfig['schedulers'].append(SingleBranchScheduler(
            builderNames=[self.name],
            change_filter=ChangeFilter(filter_fn=partial(is_dir_in_change, paths)),
            name=scheduler_name(self, 'filter-' + hashify(''.join(paths))),
            treeStableTimer=60))
